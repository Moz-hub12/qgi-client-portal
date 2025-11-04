from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
import os

from ..models.admin import Admin, db

admin_setup_bp = Blueprint('admin_setup', __name__)


@admin_setup_bp.route('/setup/fix-permissions', methods=['POST'])
@jwt_required()
def fix_admin_permissions():
    """
    Fix admin permissions for the logged-in admin user.
    This endpoint allows admins to set their own permissions without shell access.
    
    Security: Only works if:
    1. User is authenticated as admin
    2. User is a super_admin OR no other admins exist (first-time setup)
    """
    try:
        claims = get_jwt()
        
        # Verify this is an admin user
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        admin_id = claims.get('admin_id')
        admin = Admin.query.get(admin_id)
        
        if not admin:
            return jsonify({'error': 'Admin not found'}), 404
        
        # Security check: Only allow if super_admin or first admin
        total_admins = Admin.query.count()
        
        if admin.role != 'super_admin' and total_admins > 1:
            return jsonify({
                'error': 'Only super admins can fix permissions',
                'message': 'Contact a super admin to update your permissions'
            }), 403
        
        # Full permissions for admin users
        full_permissions = {
            'manage_clients': True,
            'manage_portfolios': True,
            'manage_documents': True,
            'manage_announcements': True,
            'manage_support': True,
            'view_analytics': True,
            'manage_admins': True,
            'manage_compliance': True,
            'system_settings': True
        }
        
        # Get current permissions
        current_permissions = admin.get_permissions()
        
        # Set new permissions
        admin.set_permissions(full_permissions)
        db.session.commit()
        
        return jsonify({
            'message': 'Permissions updated successfully',
            'admin': {
                'id': admin.id,
                'username': admin.username,
                'role': admin.role
            },
            'previous_permissions': current_permissions,
            'new_permissions': full_permissions,
            'instructions': 'Please log out and log back in for changes to take effect'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_setup_bp.route('/setup/fix-all-permissions', methods=['POST'])
def fix_all_admin_permissions():
    """
    Fix permissions for ALL admin users.
    This is a one-time setup endpoint that can be called without authentication.
    
    Security: Only works if a secret key is provided in the request.
    Set ADMIN_SETUP_KEY in environment variables.
    """
    try:
        # Get setup key from request
        data = request.get_json() or {}
        provided_key = data.get('setup_key') or request.headers.get('X-Setup-Key')
        
        # Get expected key from environment
        expected_key = os.getenv('ADMIN_SETUP_KEY')
        
        # If no setup key is configured, this endpoint is disabled
        if not expected_key:
            return jsonify({
                'error': 'Setup endpoint is disabled',
                'message': 'Set ADMIN_SETUP_KEY environment variable to enable this endpoint'
            }), 403
        
        # Verify setup key
        if provided_key != expected_key:
            return jsonify({'error': 'Invalid setup key'}), 403
        
        # Get all admins
        admins = Admin.query.all()
        
        if not admins:
            return jsonify({
                'error': 'No admin users found',
                'message': 'Create an admin user first'
            }), 404
        
        # Full permissions
        full_permissions = {
            'manage_clients': True,
            'manage_portfolios': True,
            'manage_documents': True,
            'manage_announcements': True,
            'manage_support': True,
            'view_analytics': True,
            'manage_admins': True,
            'manage_compliance': True,
            'system_settings': True
        }
        
        # Update all admins
        updated_admins = []
        for admin in admins:
            admin.set_permissions(full_permissions)
            updated_admins.append({
                'username': admin.username,
                'role': admin.role,
                'permissions': full_permissions
            })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Updated permissions for {len(admins)} admin(s)',
            'admins': updated_admins,
            'instructions': 'All admins should log out and log back in'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_setup_bp.route('/setup/check-permissions', methods=['GET'])
@jwt_required()
def check_admin_permissions():
    """Check current admin permissions"""
    try:
        claims = get_jwt()
        
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        admin_id = claims.get('admin_id')
        admin = Admin.query.get(admin_id)
        
        if not admin:
            return jsonify({'error': 'Admin not found'}), 404
        
        return jsonify({
            'admin': {
                'id': admin.id,
                'username': admin.username,
                'email': admin.email,
                'role': admin.role,
                'is_active': admin.is_active
            },
            'permissions': admin.get_permissions(),
            'has_all_permissions': all([
                admin.has_permission('manage_clients'),
                admin.has_permission('manage_portfolios'),
                admin.has_permission('view_analytics'),
                admin.has_permission('manage_compliance')
            ])
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

