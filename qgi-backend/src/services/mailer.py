# src/services/mailer.py
from __future__ import annotations
import os, json, logging
from typing import Mapping, Optional, Sequence
import requests

SENDGRID_API = "https://api.sendgrid.com/v3/mail/send"
DEFAULT_TIMEOUT_S = int(os.getenv("SENDGRID_TIMEOUT_SECONDS", "10"))

class MailerError(RuntimeError):
    pass

def _bearer() -> str:
    key = (os.getenv("SENDGRID_API_KEY") or "").strip()
    if not key or not key.startswith("SG."):
        raise MailerError("SENDGRID_API_KEY missing or invalid (must start with 'SG.')")
    return f"Bearer {key}"

def _normalize_recipients(to) -> list[dict]:
    if not to:
        return []
    if isinstance(to, str):
        parts = [p.strip() for p in to.split(",") if p.strip()]
        return [{"email": p} for p in parts]
    if isinstance(to, Sequence):
        return [{"email": str(x)} for x in to if str(x).strip()]
    return [{"email": str(to)}]

def _request(payload: dict) -> tuple[int, str]:
    headers = {
        "Authorization": _bearer(),
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(
            SENDGRID_API,
            headers=headers,
            data=json.dumps(payload),
            timeout=DEFAULT_TIMEOUT_S,
        )
        return resp.status_code, resp.text[:2000]
    except requests.Timeout:
        logging.error("SendGrid request timed out after %ss", DEFAULT_TIMEOUT_S)
        return 599, "timeout"
    except requests.RequestException as e:
        logging.error("SendGrid request error: %s", e)
        return 598, str(e)

def send_plain(*, to, subject: str, text: str) -> bool:
    payload = {
        "from": {
            "email": os.getenv("FROM_EMAIL", "noreply@qgi.capital"),
            "name": os.getenv("FROM_NAME", "QGI Client Portal"),
        },
        "personalizations": [{"to": _normalize_recipients(to)}],
        "subject": subject,
        "content": [{"type": "text/plain", "value": text}],
    }
    status, body = _request(payload)
    if status != 202:
        logging.error("SendGrid send_plain failed: status=%s body=%s", status, body)
        return False
    return True

def send_template(*, to, template_id: str, dynamic_data: Optional[Mapping] = None, subject_fallback: Optional[str] = None) -> bool:
    payload = {
        "from": {
            "email": os.getenv("FROM_EMAIL", "noreply@qgi.capital"),
            "name": os.getenv("FROM_NAME", "QGI Client Portal"),
        },
        "template_id": template_id,
        "personalizations": [{
            "to": _normalize_recipients(to),
            **({"dynamic_template_data": dict(dynamic_data)} if dynamic_data else {}),
        }],
    }
    if subject_fallback:
        payload["subject"] = subject_fallback
    status, body = _request(payload)
    if status != 202:
        logging.error("SendGrid send_template failed: status=%s body=%s", status, body)
        return False
    return True
