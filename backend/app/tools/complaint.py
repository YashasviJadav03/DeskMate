"""
Complaint Tool — logs customer complaints to SQLite.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from app.config import settings


# ── Tool schema (for LLM function calling) ──────────────

TOOL_SCHEMA = {
    "name": "log_complaint",
    "description": "Log a customer complaint or issue report. Creates a support ticket and returns the ticket ID.",
    "parameters": {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "Brief subject/title of the complaint (e.g., 'Late Delivery', 'Damaged Product')",
            },
            "description": {
                "type": "string",
                "description": "Detailed description of the complaint",
            },
        },
        "required": ["subject", "description"],
    },
}


# ── Database setup ───────────────────────────────────────


def _init_db() -> None:
    """Create the tickets table if it doesn't exist."""
    conn = sqlite3.connect(settings.tickets_db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            priority TEXT NOT NULL DEFAULT 'Normal',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ── Tool implementation ──────────────────────────────────


def log_complaint(subject: str, description: str) -> dict:
    """
    Log a complaint and return the ticket details.
    """
    _init_db()

    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()

    # Determine priority from keywords
    priority = "Normal"
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in ["urgent", "immediately", "asap", "critical"]):
        priority = "High"
    elif any(kw in desc_lower for kw in ["damaged", "broken", "wrong item", "missing"]):
        priority = "High"

    conn = sqlite3.connect(settings.tickets_db_path)
    conn.execute(
        """
        INSERT INTO tickets (id, subject, description, status, priority, created_at, updated_at)
        VALUES (?, ?, ?, 'Open', ?, ?, ?)
        """,
        (ticket_id, subject, description, priority, now, now),
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "ticket_id": ticket_id,
        "subject": subject,
        "status": "Open",
        "priority": priority,
        "message": f"Your complaint has been logged successfully. Your ticket ID is {ticket_id}. Our team will review it within 1-3 business days.",
    }
