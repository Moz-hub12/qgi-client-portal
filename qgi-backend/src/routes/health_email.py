# src/routes/health_email.py
from flask import Blueprint, jsonify
from src.services.mailer import send_plain

bp = Blueprint("health_email", __name__)

@bp.get("/health/email")
def health_email():
    import os
    to = os.getenv("HEALTH_EMAIL_TO") or os.getenv("ADMIN_ALERT_TO") or "admin@quantumgrowthinvestments.com"
    ok = send_plain(to, "QGI Email Health", "This is a health check.")
    return jsonify({"ok": ok})
