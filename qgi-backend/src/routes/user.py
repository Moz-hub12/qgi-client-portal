# at top of file (ensure these are present)
import os, urllib.parse
from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.services.notifications import (
    send_client_invite, send_kyc_update, send_admin_alert, send_welcome_email
)

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({'error': 'username and email are required'}), 400

    # Uniqueness guard
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email already exists'}), 409

    # Create user
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()

    # Links
    base = os.getenv('FRONTEND_URL', 'https://quantumgrowthinvestments.com').rstrip('/')
    invite_link = f"{base}/portal/join?email={urllib.parse.quote(email)}"
    portal_link = f"{base}/portal"

    # Toggles
    SEND_INVITE = (os.getenv('SEND_INVITE_ON_CREATE', '1') == '1')
    SEND_WELCOME = (os.getenv('SEND_WELCOME_ON_CREATE', '1') == '1')

    # Branding
    support_email = os.getenv('SUPPORT_EMAIL', 'support@quantumgrowthinvestments.com')
    brand_name = os.getenv('BRAND_NAME', 'QGI Client Portal')
    logo_url = os.getenv('LOGO_URL', '')

    # Send invite (optional)
    if SEND_INVITE:
        try:
            send_client_invite(
                email, username or 'Investor', invite_link,
                cta_text="Accept Invite", brand_name=brand_name, logo_url=logo_url
            )
        except Exception as e:
            try:
                send_admin_alert(None, "New user created (invite email failed)",
                                 f"User {user.id} <{email}> created, but invite email failed: {e}")
            except Exception:
                pass

    # Send welcome (optional)
    if SEND_WELCOME:
        try:
            send_welcome_email(
                email, username or 'Investor',
                portal_link=portal_link, support_email=support_email,
                cta_text="Open your portal", brand_name=brand_name, logo_url=logo_url
            )
        except Exception:
            pass

    # Admin alert (non-blocking)
    try:
        send_admin_alert(None, "New user created",
                         f"User {user.id} created: username={username}, email={email}")
    except Exception:
        pass

    return jsonify(user.to_dict()), 201
