from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import io
import csv

from ..models.admin import Admin
from ..models.user import User, InvestorData, db

admin_reports_bp = Blueprint('admin_reports', __name__)


def require_admin_permission(permission):
    """Decorator to check admin permissions"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            admin_id = claims.get('admin_id')
            admin = Admin.query.get(admin_id)
            
            if not admin or not admin.is_active:
                return jsonify({'error': 'Admin not found'}), 404
            
            if not admin.has_permission(permission):
                return jsonify({'error': f'Permission {permission} required'}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


@admin_reports_bp.route('/reports/dashboard', methods=['GET'])
@jwt_required()
@require_admin_permission('view_analytics')
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Total clients
        total_clients = User.query.filter_by(is_investor=True).count()
        
        # Active clients (with portfolio data)
        active_clients = db.session.query(User).join(InvestorData).filter(
            User.is_investor == True
        ).count()
        
        # Total AUM
        total_aum = db.session.query(
            func.sum(InvestorData.current_value)
        ).scalar() or 0.0
        
        # Total contributions
        total_contributions = db.session.query(
            func.sum(InvestorData.total_contributions)
        ).scalar() or 0.0
        
        # Total P&L
        total_pnl = db.session.query(
            func.sum(InvestorData.profit_loss)
        ).scalar() or 0.0
        
        # Calculate MTD return
        mtd_return = (total_pnl / total_contributions * 100) if total_contributions > 0 else 0.0
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_clients = User.query.filter(
            User.is_investor == True,
            User.created_at >= week_ago
        ).count()
        
        # Compliance flags
        compliance_flags = User.query.filter(
            User.is_investor == True,
            User.kyc_status.in_(['pending', 'flagged', 'rejected'])
        ).count()
        
        return jsonify({
            'stats': {
                'total_clients': total_clients,
                'active_clients': active_clients,
                'total_aum': float(total_aum),
                'total_contributions': float(total_contributions),
                'total_pnl': float(total_pnl),
                'mtd_return': round(mtd_return, 2),
                'new_clients_this_week': new_clients,
                'compliance_flags': compliance_flags
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_reports_bp.route('/reports/equity-curve', methods=['GET'])
@jwt_required()
@require_admin_permission('view_analytics')
def get_equity_curve():
    """Get equity curve data for all portfolios"""
    try:
        # Get all investor data with NAV history
        investors = InvestorData.query.all()
        
        # Aggregate NAV history by date
        equity_curve = {}
        
        for investor in investors:
            nav_history = investor.nav_history or []
            for entry in nav_history:
                date = entry.get('date', '')
                value = entry.get('value', 0.0)
                
                if date:
                    if date not in equity_curve:
                        equity_curve[date] = 0.0
                    equity_curve[date] += value
        
        # Convert to sorted list
        data_points = [
            {'date': date, 'value': value}
            for date, value in sorted(equity_curve.items())
        ]
        
        # If no historical data, use current values
        if not data_points:
            total_current = sum(inv.current_value for inv in investors)
            data_points = [{
                'date': datetime.utcnow().isoformat(),
                'value': total_current
            }]
        
        return jsonify({
            'equity_curve': data_points,
            'data_points': len(data_points),
            'last_update': data_points[-1]['date'] if data_points else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_reports_bp.route('/reports/pnl-by-instrument', methods=['GET'])
@jwt_required()
@require_admin_permission('view_analytics')
def get_pnl_by_instrument():
    """Get P&L breakdown by instrument"""
    try:
        # Get all investor data
        investors = InvestorData.query.all()
        
        # Aggregate by instrument
        instruments = {}
        
        for investor in investors:
            holdings = investor.holdings or []
            for holding in holdings:
                instrument = holding.get('instrument', 'Unknown')
                pnl = holding.get('profit_loss', 0.0)
                
                if instrument not in instruments:
                    instruments[instrument] = {
                        'instrument': instrument,
                        'total_pnl': 0.0,
                        'count': 0
                    }
                
                instruments[instrument]['total_pnl'] += pnl
                instruments[instrument]['count'] += 1
        
        # Convert to list and sort by P&L
        pnl_data = sorted(
            instruments.values(),
            key=lambda x: x['total_pnl'],
            reverse=True
        )
        
        return jsonify({
            'pnl_by_instrument': pnl_data,
            'instruments': len(pnl_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_reports_bp.route('/reports/raw-snapshot', methods=['GET'])
@jwt_required()
@require_admin_permission('view_analytics')
def get_raw_snapshot():
    """Get raw portfolio snapshot data"""
    try:
        # Get all users with investor data
        users = db.session.query(User, InvestorData).join(
            InvestorData, User.id == InvestorData.user_id
        ).filter(User.is_investor == True).all()
        
        snapshot = []
        for user, investor_data in users:
            snapshot.append({
                'investor_id': user.investor_id,
                'name': user.name,
                'email': user.email,
                'current_value': float(investor_data.current_value),
                'total_contributions': float(investor_data.total_contributions),
                'profit_loss': float(investor_data.profit_loss),
                'return_pct': round(
                    (investor_data.profit_loss / investor_data.total_contributions * 100)
                    if investor_data.total_contributions > 0 else 0.0,
                    2
                ),
                'kyc_status': user.kyc_status,
                'last_report_date': investor_data.last_report_date.isoformat()
                    if investor_data.last_report_date else None
            })
        
        return jsonify({
            'snapshot': snapshot,
            'total_records': len(snapshot),
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_reports_bp.route('/reports/export/csv', methods=['GET'])
@jwt_required()
@require_admin_permission('view_analytics')
def export_csv():
    """Export portfolio data as CSV"""
    try:
        report_type = request.args.get('type', 'snapshot')
        
        # Get data based on report type
        if report_type == 'snapshot':
            users = db.session.query(User, InvestorData).join(
                InvestorData, User.id == InvestorData.user_id
            ).filter(User.is_investor == True).all()
            
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Investor ID', 'Name', 'Email', 'Current Value',
                'Total Contributions', 'Profit/Loss', 'Return %',
                'KYC Status', 'Last Report Date'
            ])
            
            # Write data
            for user, investor_data in users:
                return_pct = round(
                    (investor_data.profit_loss / investor_data.total_contributions * 100)
                    if investor_data.total_contributions > 0 else 0.0,
                    2
                )
                
                writer.writerow([
                    user.investor_id or '',
                    user.name,
                    user.email,
                    f"{investor_data.current_value:.2f}",
                    f"{investor_data.total_contributions:.2f}",
                    f"{investor_data.profit_loss:.2f}",
                    f"{return_pct:.2f}%",
                    user.kyc_status,
                    investor_data.last_report_date.strftime('%Y-%m-%d')
                        if investor_data.last_report_date else ''
                ])
            
            # Prepare file for download
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'qgi_portfolio_snapshot_{datetime.utcnow().strftime("%Y%m%d")}.csv'
            )
        
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_reports_bp.route('/reports/export/pdf', methods=['GET'])
@jwt_required()
@require_admin_permission('view_analytics')
def export_pdf():
    """Export portfolio report as PDF"""
    try:
        # This would require a PDF generation library
        # For now, return a placeholder
        return jsonify({
            'message': 'PDF export not yet implemented',
            'suggestion': 'Use CSV export for now'
        }), 501
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

