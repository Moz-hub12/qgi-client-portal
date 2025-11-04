from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
from sqlalchemy import or_, desc

from ..models.admin import Admin
from ..models.user import User, InvestorData, db
from ..models.document import Document
from ..models.support import SupportRequest

admin_clients_bp = Blueprint('admin_clients', __name__)

ROLE_PERMS = {
    'super_admin': {'manage_clients','view_reports','manage_compliance','manage_admins'},
    'admin': {'manage_clients','view_reports','manage_compliance'},
}


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

@admin_clients_bp.route('/clients', methods=['GET'])
@jwt_required()
@require_admin_permission('manage_clients')
def get_all_clients():
    """Get all clients with pagination and search"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
        query = User.query.filter_by(is_investor=True)
        
        # Add search filter
        if search:
            query = query.filter(
                or_(
                    User.name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    User.username.ilike(f'%{search}%'),
                    User.investor_id.ilike(f'%{search}%')
                )
            )
        
        # Add sorting
        if hasattr(User, sort_by):
            if sort_order == 'desc':
                query = query.order_by(desc(getattr(User, sort_by)))
            else:
                query = query.order_by(getattr(User, sort_by))
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        clients = []
        for user in pagination.items:
            client_data = user.to_dict()
            
            # Add investor data
            investor_data = InvestorData.query.filter_by(user_id=user.id).first()
            if investor_data:
                client_data['portfolio'] = investor_data.to_dict()
            else:
                client_data['portfolio'] = None
            
            # Add recent activity count
            recent_support = SupportRequest.query.filter_by(user_id=user.id).count()
            client_data['support_requests'] = recent_support
            
            clients.append(client_data)
        
        return jsonify({
            'clients': clients,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_clients_bp.route('/clients/<int:client_id>', methods=['GET'])
@jwt_required()
@require_admin_permission('manage_clients')
def get_client_details():
    """Get detailed client information"""
    try:
        client_id = request.view_args['client_id']
        user = User.query.get(client_id)
        
        if not user or not user.is_investor:
            return jsonify({'error': 'Client not found'}), 404
        
        client_data = user.to_dict()
        
        # Add investor data
        investor_data = InvestorData.query.filter_by(user_id=user.id).first()
        if investor_data:
            client_data['portfolio'] = investor_data.to_dict()
        
        # Add documents
        documents = Document.query.filter_by(user_id=user.id).all()
        client_data['documents'] = [doc.to_dict() for doc in documents]
        
        # Add support requests
        support_requests = SupportRequest.query.filter_by(user_id=user.id).order_by(desc(SupportRequest.created_at)).limit(10).all()
        client_data['recent_support'] = [req.to_dict() for req in support_requests]
        
        return jsonify({'client': client_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_clients_bp.route('/clients/<int:client_id>', methods=['PUT'])
@jwt_required()
@require_admin_permission('manage_clients')
def update_client():
    """Update client information"""
    try:
        client_id = request.view_args['client_id']
        user = User.query.get(client_id)
        
        if not user or not user.is_investor:
            return jsonify({'error': 'Client not found'}), 404
        
        data = request.get_json()
        
        # Update user fields
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            # Check if email is already taken
            existing = User.query.filter(User.email == data['email'], User.id != user.id).first()
            if existing:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = data['email']
        if 'investor_id' in data:
            user.investor_id = data['investor_id']
        if 'kyc_status' in data:
            user.kyc_status = data['kyc_status']
        
        # Update profile data
        if 'profile_data' in data:
            user.update_profile_data(data['profile_data'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Client updated successfully',
            'client': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_clients_bp.route('/clients/<int:client_id>/portfolio', methods=['PUT'])
@jwt_required()
@require_admin_permission('manage_portfolios')
def update_client_portfolio():
    """Update client portfolio data"""
    try:
        client_id = request.view_args['client_id']
        user = User.query.get(client_id)
        
        if not user or not user.is_investor:
            return jsonify({'error': 'Client not found'}), 404
        
        data = request.get_json()
        
        # Get or create investor data
        investor_data = InvestorData.query.filter_by(user_id=user.id).first()
        if not investor_data:
            investor_data = InvestorData(user_id=user.id)
            db.session.add(investor_data)
        
        # Update portfolio fields
        if 'current_value' in data:
            investor_data.current_value = float(data['current_value'])
        if 'total_contributions' in data:
            investor_data.total_contributions = float(data['total_contributions'])
        if 'profit_loss' in data:
            investor_data.profit_loss = float(data['profit_loss'])
        if 'last_report_date' in data:
            investor_data.last_report_date = datetime.fromisoformat(data['last_report_date'])
        if 'next_lock_date' in data:
            investor_data.next_lock_date = datetime.fromisoformat(data['next_lock_date'])
        
        # Add NAV history entry if current_value changed
        if 'current_value' in data:
            nav_entry = {
                'date': datetime.utcnow().isoformat(),
                'value': investor_data.current_value,
                'updated_by': 'admin'
            }
            investor_data.update_nav_history(nav_entry)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Portfolio updated successfully',
            'portfolio': investor_data.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_clients_bp.route('/clients', methods=['POST'])
@jwt_required()
@require_admin_permission('manage_clients')
def create_client():
    """Create new client"""
    try:
        data = request.get_json()
        
        required_fields = ['username', 'email', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            or_(User.username == data['username'], User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            name=data['name'],
            is_investor=True,
            investor_id=data.get('investor_id'),
            kyc_status=data.get('kyc_status', 'pending')
        )
        
        # Add profile data if provided
        if 'profile_data' in data:
            user.update_profile_data(data['profile_data'])
        
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create initial investor data if portfolio info provided
        if 'portfolio' in data:
            portfolio = data['portfolio']
            investor_data = InvestorData(
                user_id=user.id,
                current_value=portfolio.get('current_value', 0.0),
                total_contributions=portfolio.get('total_contributions', 0.0),
                profit_loss=portfolio.get('profit_loss', 0.0)
            )
            db.session.add(investor_data)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Client created successfully',
            'client': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_clients_bp.route('/clients/<int:client_id>', methods=['DELETE'])
@jwt_required()
@require_admin_permission('manage_clients')
def delete_client():
    """Delete client (soft delete - deactivate)"""
    try:
        client_id = request.view_args['client_id']
        user = User.query.get(client_id)
        
        if not user or not user.is_investor:
            return jsonify({'error': 'Client not found'}), 404
        
        # Soft delete - just mark as inactive
        user.is_investor = False
        db.session.commit()
        
        return jsonify({'message': 'Client deactivated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

