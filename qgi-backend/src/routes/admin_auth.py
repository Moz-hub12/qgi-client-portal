from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
import secrets
import os
from marshmallow import Schema, fields, validate, ValidationError

from ..models.admin import Admin, AdminSession, db
from ..models.user import User, InvestorData

admin_auth_bp = Blueprint('admin_auth', __name__)

class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    password = fields.Str(required=True, validate=validate.Length(min=6))


@admin_auth_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin login with username/password"""
    try:
        raw = request.get_json() or {}
        try:
            data = LoginSchema().load(raw)
        except ValidationError as ve:
            return jsonify({'error': ve.messages}), 422
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find admin user
        admin = Admin.query.filter_by(username=username, is_active=True).first()
        
        if not admin or not admin.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update last login
        admin.last_login = datetime.utcnow()
        
        # Create session token
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=8)  # 8 hour sessions
        
        admin_session = AdminSession(
            admin_id=admin.id,
            session_token=session_token,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            expires_at=expires_at
        )
        
        db.session.add(admin_session)
        db.session.commit()
        
        # Create JWT token with admin role
        additional_claims = {
            'role': 'admin',
            'admin_id': admin.id,
            'session_token': session_token
        }
        
        access_token = create_access_token(
            identity=str(admin.id),
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=8)
        )
        
        return jsonify({
            'access_token': access_token,
            'admin': admin.to_dict(),
            'expires_at': expires_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def admin_logout():
    """Admin logout - invalidate session"""
    try:
        claims = get_jwt()
        session_token = claims.get('session_token')
        
        if session_token:
            session = AdminSession.query.filter_by(session_token=session_token).first()
            if session:
                session.is_active = False
                db.session.commit()
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_admin_profile():
    """Get current admin profile"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        admin_id = int(get_jwt_identity())
        admin = Admin.query.get(admin_id)
        
        if not admin or not admin.is_active:
            return jsonify({'error': 'Admin not found'}), 404
        
        return jsonify({'admin': admin.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_auth_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_admin_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get basic statistics
        total_clients = User.query.filter_by(is_investor=True).count()
        active_clients = User.query.filter_by(is_investor=True).count()  # All are active for now
        
        # Get portfolio statistics
        total_portfolio_value = db.session.query(db.func.sum(InvestorData.current_value)).scalar() or 0
        total_contributions = db.session.query(db.func.sum(InvestorData.total_contributions)).scalar() or 0
        
        # Calculate profit/loss manually since it's a computed property
        total_profit_loss = 0
        if total_portfolio_value and total_contributions:
            total_profit_loss = float(total_portfolio_value) - float(total_contributions)
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_clients = User.query.filter(
            User.is_investor == True,
            User.created_at >= thirty_days_ago
        ).count()
        
        stats = {
            'clients': {
                'total': total_clients,
                'active': active_clients,
                'recent': recent_clients
            },
            'portfolio': {
                'total_value': total_portfolio_value,
                'total_contributions': total_contributions,
                'total_profit_loss': total_profit_loss,
                'average_return': (total_profit_loss / float(total_contributions) * 100) if total_contributions > 0 else 0
            },
            'activity': {
                'new_clients_30d': recent_clients,
                'last_updated': datetime.utcnow().isoformat()
            }
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_auth_bp.route('/create-admin', methods=['POST'])
def create_admin():
    """Create initial admin user (only if no admins exist)"""
    try:
        # Check if any admins exist
        existing_admin = Admin.query.first()
        if existing_admin:
            return jsonify({'error': 'Admin users already exist'}), 400
        
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        
        if not all([username, email, name, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Create admin user
        admin = Admin(
            username=username,
            email=email,
            name=name,
            role='super_admin'
        )
        admin.set_password(password)
        
        # Set default permissions
        default_permissions = {
            'manage_clients': True,
            'manage_portfolios': True,
            'manage_documents': True,
            'manage_announcements': True,
            'manage_support': True,
            'view_analytics': True,
            'manage_admins': True
        }
        admin.set_permissions(default_permissions)
        
        db.session.add(admin)
        db.session.commit()
        
        return jsonify({
            'message': 'Admin user created successfully',
            'admin': admin.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_access_token():
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        admin_id = get_jwt_identity()
        new_access = create_access_token(identity=str(admin_id), additional_claims={'role': 'admin'}, fresh=False)
        return jsonify({'access_token': new_access}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
