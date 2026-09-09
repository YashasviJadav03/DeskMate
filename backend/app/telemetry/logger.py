"""
Structured logger — records every query through the pipeline to SQLite.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.models import ChatResponse, LogEntry


# ── Database setup ───────────────────────────────────────


def _init_db() -> None:
    """Create the query_logs table if it doesn't exist."""
    conn = sqlite3.connect(settings.logs_db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            session_id TEXT NOT NULL,
            query TEXT NOT NULL,
            route TEXT NOT NULL,
            agent TEXT NOT NULL,
            tool_called TEXT,
            tool_input TEXT,
            tool_output TEXT,
            response TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            tokens_used INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


# Ensure table exists on module import
_init_db()


# ── Public API ───────────────────────────────────────────


def log_query(query: str, response: ChatResponse, tokens_used: int = 0) -> int:
    """
    Log a processed query and its response.

    Returns the log entry ID.
    """
    conn = sqlite3.connect(settings.logs_db_path)
    cursor = conn.execute(
        """
        INSERT INTO query_logs
            (timestamp, session_id, query, route, agent,
             tool_called, tool_input, tool_output,
             response, latency_ms, tokens_used)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            response.session_id,
            query,
            response.trace.route,
            response.trace.agent,
            response.trace.tool_called,
            json.dumps(response.trace.tool_input) if response.trace.tool_input else None,
            json.dumps(response.trace.tool_output) if response.trace.tool_output else None,
            response.response,
            response.trace.latency_ms,
            tokens_used,
        ),
    )
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id


def get_logs(
    limit: int = 50,
    session_id: Optional[str] = None,
) -> list[LogEntry]:
    """
    Retrieve recent logs, optionally filtered by session_id.
    """
    conn = sqlite3.connect(settings.logs_db_path)
    conn.row_factory = sqlite3.Row

    if session_id:
        rows = conn.execute(
            "SELECT * FROM query_logs WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM query_logs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    conn.close()

    return [
        LogEntry(
            id=row["id"],
            timestamp=row["timestamp"],
            session_id=row["session_id"],
            query=row["query"],
            route=row["route"],
            agent=row["agent"],
            tool_called=row["tool_called"],
            tool_input=row["tool_input"],
            tool_output=row["tool_output"],
            response=row["response"],
            latency_ms=row["latency_ms"],
            tokens_used=row["tokens_used"],
        )
        for row in rows
    ]


def get_log_stats() -> dict:
    """Get summary statistics from the logs."""
    conn = sqlite3.connect(settings.logs_db_path)

    total = conn.execute("SELECT COUNT(*) FROM query_logs").fetchone()[0]
    informational = conn.execute(
        "SELECT COUNT(*) FROM query_logs WHERE route = 'informational'"
    ).fetchone()[0]
    actionable = conn.execute(
        "SELECT COUNT(*) FROM query_logs WHERE route = 'actionable'"
    ).fetchone()[0]
    avg_latency = conn.execute(
        "SELECT AVG(latency_ms) FROM query_logs"
    ).fetchone()[0]

    conn.close()

    return {
        "total_queries": total,
        "informational": informational,
        "actionable": actionable,
        "avg_latency_ms": round(avg_latency, 2) if avg_latency else 0,
    }
