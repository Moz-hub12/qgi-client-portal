# example: src/routes/admin_notifications.py
from flask import Blueprint, jsonify, request
from src.services.mailer import send_plain, send_template

bp = Blueprint("admin_notifications", __name__, url_prefix="/api/admin/notify")

@bp.post("/test")
def send_test():
    data = request.get_json(force=True, silent=True) or {}
    to = data.get("to")
    if not to:
        return jsonify({"error": "missing 'to'"}), 400

    ok = send_plain(
        to=to,
        subject="QGI test",
        text="Hello from QGI mailer",
        html="<p>Hello from <b>QGI</b> mailer</p>",
    )
    return jsonify({"ok": ok}), (200 if ok else 502)

@bp.post("/template")
def send_template_route():
    data = request.get_json(force=True, silent=True) or {}
    to = data.get("to")
    template_id = data.get("template_id")  # your SendGrid dynamic template id
    dyn = data.get("data") or {}
    if not (to and template_id):
        return jsonify({"error": "missing 'to' or 'template_id'"}), 400
    ok = send_template(to=to, template_id=template_id, dynamic_data=dyn, subject_fallback="Notification")
    return jsonify({"ok": ok}), (200 if ok else 502)
