# src/routes/notify_test.py
from __future__ import annotations
import os
from flask import Blueprint, request, jsonify
from src.services import notifications as N

bp = Blueprint("notify_test", __name__)

def _ok():
    key = os.getenv("NOTIFY_TEST_KEY")
    if not key:
        return False
    return request.headers.get("x-notify-key") == key

@bp.post("/notify/test/invite")
def test_invite():
    if not _ok():
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    data = request.get_json(force=True, silent=True) or {}
    to = data.get("to")
    first_name = data.get("first_name", "Investor")
    link = data.get("invite_link", "https://quantumgrowthinvestments.com/portal/join")
    ok = N.send_client_invite(to, first_name, link)
    return jsonify({"ok": ok})

@bp.post("/notify/test/kyc")
def test_kyc():
    if not _ok():
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    data = request.get_json(force=True, silent=True) or {}
    to = data.get("to")
    name = data.get("name", "Investor")
    link = data.get("kyc_link", "https://quantumgrowthinvestments.com/portal/kyc")
    ok = N.send_kyc_update(to, name, link)
    return jsonify({"ok": ok})

@bp.post("/notify/test/admin-alert")
def test_admin_alert():
    if not _ok():
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    data = request.get_json(force=True, silent=True) or {}
    to = data.get("to")  # optional; falls back to ADMIN_ALERT_TO
    subject = data.get("subject", "Test Admin Alert")
    message = data.get("message", "This is a test admin alert from /notify/test.")
    ok = N.send_admin_alert(to, subject, message)
    return jsonify({"ok": ok})
