"""
Pydantic schemas for API requests and responses.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ── Request ──────────────────────────────────────────────


class ChatRequest(BaseModel):
    """Incoming chat message from the user."""

    query: str = Field(..., min_length=1, description="The user's query text")
    session_id: Optional[str] = Field(
        None, description="Session ID to group conversation turns"
    )


# ── Trace (sub-model) ───────────────────────────────────


class AgentTrace(BaseModel):
    """Diagnostic trace showing how the query was handled."""

    route: str = Field(..., description="'informational' or 'actionable'")
    agent: str = Field(..., description="Agent that handled the query")
    tool_called: Optional[str] = Field(None, description="Tool name if any")
    tool_input: Optional[dict] = Field(None, description="Tool input params")
    tool_output: Optional[dict] = Field(None, description="Tool output")
    sources: Optional[list[str]] = Field(
        None, description="Retrieved source documents (for informational)"
    )
    latency_ms: float = Field(..., description="End-to-end latency in ms")


# ── Response ─────────────────────────────────────────────


class ChatResponse(BaseModel):
    """Response returned to the frontend."""

    response: str = Field(..., description="The agent's answer text")
    trace: AgentTrace
    session_id: str


# ── Log entry (for /logs endpoint) ──────────────────────


class LogEntry(BaseModel):
    """A single row from the query_logs table."""

    id: int
    timestamp: str
    session_id: str
    query: str
    route: str
    agent: str
    tool_called: Optional[str] = None
    tool_input: Optional[str] = None
    tool_output: Optional[str] = None
    response: str
    latency_ms: float
    tokens_used: int
