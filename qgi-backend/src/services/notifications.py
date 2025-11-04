# src/services/notifications.py
from __future__ import annotations
import os
from typing import Optional
from src.services.mailer import send_template, send_plain

# Read your template IDs from env so you can change them without code changes
TPL_CLIENT_INVITE = os.getenv("SG_TPL_CLIENT_INVITE")      # e.g. d-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
TPL_KYC_UPDATE    = os.getenv("SG_TPL_KYC_UPDATE")         # e.g. d-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
TPL_ADMIN_ALERT   = os.getenv("SG_TPL_ADMIN_ALERT")        # e.g. d-cccccccccccccccccccccccccccccccc
TPL_WELCOME       = os.getenv("SG_TPL_WELCOME")            # e.g. d-dddddddddddddddddddddddddddddddd        # e.g. d-cccccccccccccccccccccccccccccccc
ADMIN_FALLBACK_TO = os.getenv("ADMIN_ALERT_TO")            # optional default catch-all for admin alerts
SUPPORT_EMAIL   = os.getenv("SUPPORT_EMAIL", "support@quantumgrowthinvestments.com")
BRAND_NAME      = os.getenv("BRAND_NAME", "QGI Client Portal")
LOGO_URL        = os.getenv("LOGO_URL", "")
FRONTEND_URL    = os.getenv("FRONTEND_URL", "https://quantumgrowthinvestments.com")

def send_client_invite(to_email: str, first_name: str, invite_link: str) -> bool:
    """
    Sends a client invite with a CTA button/link.
    Template variables required:
      - first_name (string)
      - invite_link (url)
      - support_email (string, optional)
    """
    if not TPL_CLIENT_INVITE:
        # If no template configured, fall back to a plain text version
        subject = "You're invited to Quantum Growth Investments"
        text = f"Hi {first_name},\n\nYou're invited to join QGI.\nStart here: {invite_link}\n\n— QGI Team"
        return send_plain(to=to_email, subject=subject, text=text)

    return send_template(
        to=to_email,
        template_id=TPL_CLIENT_INVITE,
        dynamic_data={
            "first_name": first_name,
            "cta_text": "Accept Invite",
            "brand_name": BRAND_NAME,
            "portal_link": invite_link,
            "logo_url": LOGO_URL,
            "invite_link": invite_link,
            "support_email": SUPPORT_EMAIL,
        },
        subject_fallback="You're invited to Quantum Growth Investments",
    )


def send_welcome_email(to_email: str, name: str) -> bool:
    """
    Sends a simple welcome email with onboarding info.
    Template variables required:
      - name (string)
    """
    from src.services.mailer import send_template, send_plain
    recipients = to_email or ADMIN_FALLBACK_TO
    if not recipients:
        return False

    if not TPL_WELCOME:
        # Fallback plain message
        subject = "Welcome to QGI"
        text = f"Hi {name},\n\nWelcome to Quantum Growth Investments. Your account has been created.\n\n— QGI Team"
        return send_plain(to=recipients, subject=subject, text=text)

    return send_template(
        to=recipients,
        template_id=TPL_WELCOME,
        dynamic_data={
            "name": name or "Investor",
        },
        subject_fallback="Welcome to QGI",
    )

def send_kyc_update(to_email: str, first_name: str, status: str, dashboard_url: str) -> bool:
    """
    Notifies a client about a KYC status change.
    Template variables required:
      - first_name (string)
      - kyc_status (string)  # e.g., 'approved', 'pending', 'needs_action'
      - dashboard_url (url)
    """
    if not TPL_KYC_UPDATE:
        subject = "Your KYC status has changed"
        text = f"Hi {first_name},\n\nYour KYC status is now: {status}.\nView details: {dashboard_url}\n\n— QGI Team"
        return send_plain(to=to_email, subject=subject, text=text)

    return send_template(
        to=to_email,
        template_id=TPL_KYC_UPDATE,
        dynamic_data={
            "first_name": first_name,
            "cta_text": "View Dashboard",
            "brand_name": BRAND_NAME,
            "portal_link": dashboard_url,
            "logo_url": LOGO_URL,
            "kyc_status": status,
            "dashboard_url": dashboard_url,
        },
        subject_fallback="Your KYC status was updated",
    )

def send_admin_alert(subject: str, message: str, to_email: Optional[str] = None) -> bool:
    """
    Sends an internal alert to admins/compliance.
    Template variables required (if using template):
      - subject (string)
      - message (string, may contain \n)
    """
    recipients = to_email or ADMIN_FALLBACK_TO
    if not recipients:
        # No recipient configured; fail gracefully
        return False

    if not TPL_ADMIN_ALERT:
        return send_plain(to=recipients, subject=subject, text=message)

    return send_template(
        to=recipients,
        template_id=TPL_ADMIN_ALERT,
        dynamic_data={
            "subject": subject,
            "message": message,
        },
        subject_fallback=subject or "QGI Admin Alert",
    )
