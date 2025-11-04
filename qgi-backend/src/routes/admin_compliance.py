from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
from sqlalchemy import or_, desc

from ..models.admin import Admin
from ..models.user import User, db
from ..models.document import Document

admin_compliance_bp = Blueprint('admin_compliance', __name__)


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


@admin_compliance_bp.route('/compliance/flags', methods=['GET'])
@jwt_required()
@require_admin_permission('manage_compliance')
def get_compliance_flags():
    """Get all compliance flags and reviews"""
    try:
        # Get query parameters
        status_filter = request.args.get('status')  # 'pending', 'reviewed', 'flagged'
        search = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query for users with KYC issues or pending reviews
        query = User.query.filter_by(is_investor=True)
        
        # Filter by KYC status
        if status_filter:
            if status_filter == 'pending':
                query = query.filter(User.kyc_status == 'pending')
            elif status_filter == 'flagged':
                query = query.filter(User.kyc_status.in_(['flagged', 'rejected']))
            elif status_filter == 'reviewed':
                query = query.filter(User.kyc_status == 'approved')
        else:
            # Default: show pending and flagged
            query = query.filter(User.kyc_status.in_(['pending', 'flagged', 'rejected']))
        
        # Add search filter
        if search:
            query = query.filter(
                or_(
                    User.name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    User.investor_id.ilike(f'%{search}%')
                )
            )
        
        # Order by created date (newest first)
        query = query.order_by(desc(User.created_at))
        
        # Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        flags = []
        for user in pagination.items:
            # Get user's documents
            documents = Document.query.filter_by(user_id=user.id).all()
            
            flag_data = {
                'id': user.id,
                'client_name': user.name,
                'client_email': user.email,
                'investor_id': user.investor_id,
                'type': 'KYC Review',
                'severity': get_severity_from_status(user.kyc_status),
                'status': user.kyc_status,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                'documents_count': len(documents),
                'profile_data': user.profile_data or {}
            }
            
            flags.append(flag_data)
        
        return jsonify({
            'flags': flags,
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


@admin_compliance_bp.route('/compliance/flags/<int:flag_id>', methods=['GET'])
@jwt_required()
@require_admin_permission('manage_compliance')
def get_compliance_flag_details(flag_id):
    """Get detailed information about a compliance flag"""
    try:
        user = User.query.get(flag_id)
        
        if not user or not user.is_investor:
            return jsonify({'error': 'Client not found'}), 404
        
        # Get all documents
        documents = Document.query.filter_by(user_id=user.id).all()
        
        flag_data = {
            'id': user.id,
            'client_name': user.name,
            'client_email': user.email,
            'investor_id': user.investor_id,
            'type': 'KYC Review',
            'severity': get_severity_from_status(user.kyc_status),
            'status': user.kyc_status,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'profile_data': user.profile_data or {},
            'documents': [doc.to_dict() for doc in documents]
        }
        
        return jsonify({'flag': flag_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_compliance_bp.route('/compliance/flags/<int:flag_id>', methods=['PUT'])
@jwt_required()
@require_admin_permission('manage_compliance')
def update_compliance_flag(flag_id):
    """Update compliance flag status"""
    try:
        user = User.query.get(flag_id)
        
        if not user or not user.is_investor:
            return jsonify({'error': 'Client not found'}), 404
        
        data = request.get_json()
        
        # Update KYC status
        if 'status' in data:
            valid_statuses = ['pending', 'approved', 'rejected', 'flagged']
            if data['status'] not in valid_statuses:
                return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
            
            user.kyc_status = data['status']
        
        # Add review notes to profile data
        if 'notes' in data:
            profile_data = user.profile_data or {}
            if 'compliance_notes' not in profile_data:
                profile_data['compliance_notes'] = []
            
            profile_data['compliance_notes'].append({
                'date': datetime.utcnow().isoformat(),
                'note': data['notes'],
                'admin_id': get_jwt().get('admin_id')
            })
            
            user.update_profile_data(profile_data)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Compliance flag updated successfully',
            'flag': {
                'id': user.id,
                'status': user.kyc_status,
                'updated_at': user.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_compliance_bp.route('/compliance/stats', methods=['GET'])
@jwt_required()
@require_admin_permission('manage_compliance')
def get_compliance_stats():
    """Get compliance statistics"""
    try:
        # Count by KYC status
        total_investors = User.query.filter_by(is_investor=True).count()
        pending_count = User.query.filter_by(is_investor=True, kyc_status='pending').count()
        approved_count = User.query.filter_by(is_investor=True, kyc_status='approved').count()
        flagged_count = User.query.filter(
            User.is_investor == True,
            User.kyc_status.in_(['flagged', 'rejected'])
        ).count()
        
        # Recent flags (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_flags = User.query.filter(
            User.is_investor == True,
            User.kyc_status.in_(['flagged', 'rejected']),
            User.updated_at >= week_ago
        ).count()
        
        return jsonify({
            'stats': {
                'total_investors': total_investors,
                'pending_review': pending_count,
                'approved': approved_count,
                'flagged': flagged_count,
                'recent_flags': recent_flags
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_severity_from_status(kyc_status):
    """Map KYC status to severity level"""
    severity_map = {
        'pending': 'medium',
        'approved': 'low',
        'flagged': 'high',
        'rejected': 'high'
    }
    return severity_map.get(kyc_status, 'medium')

