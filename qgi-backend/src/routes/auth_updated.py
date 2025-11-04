# src/routes/auth.py - UPDATED VERSION with database token storage
import os
import secrets
import datetime
import re
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.magic_link import MagicLinkToken

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/magic-link', methods=['POST'])
def send_magic_link():
    """Send magic link to user's email"""
    
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
            
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user exists, if not create one
        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user with email as username initially
            username = email.split('@')[0]
            user = User(username=username, email=email)
            db.session.add(user)
            db.session.commit()
        
        # Clean up expired tokens periodically
        MagicLinkToken.cleanup_expired()
        
        # Generate magic link token
        token = secrets.token_urlsafe(32)
        
        # Store token in database with expiration (10 minutes)
        expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        magic_token = MagicLinkToken(
            token=token,
            user_id=user.id,
            email=email,
            expires_at=expiry
        )
        db.session.add(magic_token)
        db.session.commit()
        
        # Create magic link URL
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        magic_link = f"{frontend_url}/auth/verify?token={token}"
        
        # Send email using SendGrid
        try:
            from src.services.email_service import EmailService
            
            # Check if SendGrid is configured
            sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
            
            if sendgrid_api_key and sendgrid_api_key not in ['your-sendgrid-api-key', 'your-sendgrid-api-key-here']:
                # Initialize email service and send magic link
                email_service = EmailService()
                result = email_service.send_magic_link(
                    to_email=email,
                    magic_link=magic_link,
                    user_name=user.username
                )
                
                if result.get('success'):
                    return jsonify({'message': 'Magic link sent to your email'}), 200
                else:
                    # If SendGrid fails, return magic link for development
                    current_app.logger.warning(f"SendGrid failed: {result.get('error')}")
                    return jsonify({
                        'message': 'Magic link generated (email service error)',
                        'magic_link': magic_link,
                        'token': token,
                        'error_detail': result.get('error')
                    }), 200
            else:
                # For development - return the magic link directly
                return jsonify({
                    'message': 'Magic link generated (SendGrid not configured)',
                    'magic_link': magic_link,
                    'token': token
                }), 200
                
        except Exception as e:
            # For development - return the magic link directly if email fails
            current_app.logger.error(f"Email service error: {str(e)}")
            return jsonify({
                'message': 'Magic link generated (email service unavailable)',
                'magic_link': magic_link,
                'token': token,
                'error_detail': str(e)
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"Magic link generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_magic_link():
    """Verify magic link token and return JWT"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        # Check if token exists in database
        magic_token = MagicLinkToken.query.filter_by(token=token).first()
        
        if not magic_token:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Check if token is valid (not used and not expired)
        if not magic_token.is_valid():
            if magic_token.used:
                return jsonify({'error': 'Token has already been used'}), 401
            else:
                return jsonify({'error': 'Token has expired'}), 401
        
        # Get user
        user = User.query.get(magic_token.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create JWT token
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=datetime.timedelta(days=7)
        )
        
        # Mark token as used
        magic_token.mark_as_used()
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token verification error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info from JWT"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should delete JWT)"""
    return jsonify({'message': 'Logged out successfully'}), 200

