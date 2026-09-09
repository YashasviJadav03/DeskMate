"""
DeskMate FastAPI Backend — main application entry point.

Endpoints:
    POST /chat   — Main query endpoint
    GET  /logs   — View query logs
    GET  /health — Health check
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import ChatRequest, ChatResponse, LogEntry
from app.telemetry.logger import log_query, get_logs, get_log_stats


# ── App creation ─────────────────────────────────────────

app = FastAPI(
    title="DeskMate",
    description="Multi-Agent Query Resolution System — routes queries through specialized agents backed by a vector knowledge base and tool-calling capabilities.",
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "*",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ────────────────────────────────────────────


@app.get("/")
async def root() -> dict:
    """Root endpoint providing links to Swagger docs and frontend."""
    return {
        "service": "DeskMate — Multi-Agent Query Resolution System",
        "status": "running",
        "api_docs": "http://127.0.0.1:8000/docs",
        "frontend_url": "http://127.0.0.1:5173",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a user query through the multi-agent pipeline.

    The Router Agent classifies the query, then either:
    - Retrieval Agent answers from the knowledge base (informational)
    - Action Agent calls tools to perform actions (actionable)
    """
    session_id = request.session_id or str(uuid.uuid4())

    from app.agents.orchestrator import process_query

    # Process through the agent pipeline
    response = process_query(query=request.query, session_id=session_id)

    # Log the interaction
    log_query(
        query=request.query,
        response=response,
        tokens_used=0,  # Populated by the agents
    )

    return response


@app.get("/logs", response_model=list[LogEntry])
async def logs(
    limit: int = Query(default=50, ge=1, le=500),
    session_id: Optional[str] = Query(default=None),
) -> list[LogEntry]:
    """Retrieve recent query logs, optionally filtered by session_id."""
    return get_logs(limit=limit, session_id=session_id)


@app.get("/logs/stats")
async def log_stats() -> dict:
    """Get summary statistics from query logs."""
    return get_log_stats()


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "DeskMate",
        "version": "1.0.0",
        "llm_provider": settings.llm_provider,
    }


if __name__ == "__main__":
    import uvicorn
    print("[DeskMate] Starting FastAPI server on http://127.0.0.1:8000 ...", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
