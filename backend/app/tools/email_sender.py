"""
Email Sender Tool — mock email sending (logs to console).

Swappable for real SMTP in production.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone


# ── Tool schema (for LLM function calling) ──────────────

TOOL_SCHEMA = {
    "name": "send_confirmation_email",
    "description": "Send a confirmation or notification email to a customer.",
    "parameters": {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "Recipient email address",
            },
            "subject": {
                "type": "string",
                "description": "Email subject line",
            },
            "body": {
                "type": "string",
                "description": "Email body content",
            },
        },
        "required": ["to", "subject", "body"],
    },
}


# ── Tool implementation ──────────────────────────────────


def send_confirmation_email(to: str, subject: str, body: str) -> dict:
    """
    Send a confirmation email (mock implementation).

    In production, replace with actual SMTP/SendGrid/SES integration.
    """
    # Validate email format (basic check)
    if "@" not in to or "." not in to:
        return {
            "success": False,
            "error": f"Invalid email address: {to}",
        }

    timestamp = datetime.now(timezone.utc).isoformat()

    # Mock: log the email details
    email_log = {
        "to": to,
        "subject": subject,
        "body": body,
        "sent_at": timestamp,
    }

    print(f"[email_sender] Mock email sent:")
    print(f"  To: {to}")
    print(f"  Subject: {subject}")
    print(f"  Body: {body[:100]}...")
    print(f"  Timestamp: {timestamp}")

    return {
        "success": True,
        "message": f"Confirmation email sent to {to}.",
        "email_id": f"EMAIL-{hash(to + timestamp) % 100000:05d}",
        "sent_at": timestamp,
    }
