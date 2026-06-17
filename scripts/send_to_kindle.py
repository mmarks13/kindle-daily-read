#!/usr/bin/env python3
"""Email an issue EPUB to a Kindle via Amazon's Send-to-Kindle.

Amazon delivers a personal document to a Kindle when it arrives as an email
attachment from an *approved sender address*. This sends the EPUB over Gmail SMTP
from SENDER_EMAIL, which must be on the Kindle account's Approved Personal Document
E-mail List; the recipient is the @kindle.com address in KINDLE_EMAIL.

Reads from the environment (sourced from .env by run_issue.sh):
    SENDER_EMAIL         the approved Gmail sender (also the SMTP auth user)
    KINDLE_EMAIL         the @kindle.com recipient
    GMAIL_APP_PASSWORD   a Google App Password for SENDER_EMAIL

Exits non-zero on failure so the caller can warn without aborting the run.

Usage:
    python scripts/send_to_kindle.py --epub docs/issues/semi-supervised-2026-06-16.epub
"""
from __future__ import annotations

import argparse
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epub", required=True, help="path to the EPUB to send")
    args = ap.parse_args()

    epub = Path(args.epub)
    if not epub.is_file():
        print(f"send_to_kindle: no such file: {epub}", file=sys.stderr)
        return 1

    try:
        sender = os.environ["SENDER_EMAIL"]
        recipient = os.environ["KINDLE_EMAIL"]
        password = os.environ["GMAIL_APP_PASSWORD"]
    except KeyError as e:
        print(f"send_to_kindle: missing env var {e}", file=sys.stderr)
        return 1

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = epub.stem  # Send-to-Kindle ignores subject/body; use the filename
    msg.set_content("Today's issue attached.")
    msg.add_attachment(
        epub.read_bytes(),
        maintype="application",
        subtype="epub+zip",
        filename=epub.name,
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
    except Exception as e:
        print(f"send_to_kindle: send failed: {e}", file=sys.stderr)
        return 1

    print(f"send_to_kindle: sent {epub.name} to {recipient}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
