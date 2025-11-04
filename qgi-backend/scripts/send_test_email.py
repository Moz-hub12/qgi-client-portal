#!/usr/bin/env python3
import os, argparse, json
from dotenv import load_dotenv
load_dotenv()

from src.services.notifications import send_client_invite, send_kyc_update, send_admin_alert

def main():
    ap = argparse.ArgumentParser(description="Send test emails via QGI notification service.")
    ap.add_argument("--type", choices=["invite","kyc","admin"], required=True)
    ap.add_argument("--to", required=False, help="Recipient email (optional for admin; falls back to ADMIN_ALERT_TO)")
    ap.add_argument("--name", default="Investor")
    ap.add_argument("--link", default="https://quantumgrowthinvestments.com/portal")
    ap.add_argument("--subject", default="QGI Admin Alert")
    ap.add_argument("--message", default="This is a test admin alert from CLI.")
    args = ap.parse_args()

    if args.type == "invite":
        ok = send_client_invite(args.to, args.name, args.link)
    elif args.type == "kyc":
        ok = send_kyc_update(args.to, args.name, args.link)
    else:
        ok = send_admin_alert(args.to, args.subject, args.message)

    print(json.dumps({"ok": ok}))

if __name__ == "__main__":
    main()
