
# src/routes/health_email_dry.py
from __future__ import annotations
from flask import Blueprint, jsonify
import os

bp = Blueprint("health_email_dry", __name__)

@bp.get("/health/email/dry")
def health_email_dry():
    key = os.getenv("SENDGRID_API_KEY", "")
    api_key_ok = key.startswith("SG.") and len(key) > 25
    required = {
        "FROM_EMAIL": bool(os.getenv("FROM_EMAIL")),
        "SG_TPL_CLIENT_INVITE": bool(os.getenv("SG_TPL_CLIENT_INVITE")),
        "SG_TPL_WELCOME": bool(os.getenv("SG_TPL_WELCOME")),
        "SG_TPL_ADMIN_ALERT": bool(os.getenv("SG_TPL_ADMIN_ALERT")),
    }
    return jsonify({
        "api_key_format_ok": api_key_ok,
        "required_present": required,
        "timeout_seconds": int(os.getenv("SENDGRID_TIMEOUT_SECONDS", "10")),
    }), 200
