"""
Application configuration — loaded from environment variables / .env file.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


# Resolve paths relative to this file's location (backend/app/)
_APP_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _APP_DIR.parent
_PROJECT_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    """Central configuration for DeskMate."""

    # ── LLM ──────────────────────────────────────────────
    llm_provider: str = "mock"  # "mock" or "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    # ── Embeddings ───────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"

    # ── Paths ────────────────────────────────────────────
    chroma_db_path: str = str(_PROJECT_ROOT / "data" / "chroma_db")
    logs_db_path: str = str(_PROJECT_ROOT / "data" / "logs.db")
    tickets_db_path: str = str(_PROJECT_ROOT / "data" / "tickets.db")
    docs_path: str = str(_PROJECT_ROOT / "data" / "docs")

    # ── Retrieval ────────────────────────────────────────
    retrieval_top_k: int = 5
    chunk_size: int = 500
    chunk_overlap: int = 50

    # ── Server ───────────────────────────────────────────
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = str(_PROJECT_ROOT / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton instance — import this everywhere
settings = Settings()
