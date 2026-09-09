"""
Ingestion script — reads documents from data/docs/, chunks them,
generates embeddings, and stores them in ChromaDB.

Usage:
    cd backend
    python -m app.knowledge.ingest
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add backend/ to path so we can import app.*
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_BACKEND_DIR))

from app.config import settings
from app.knowledge.chunker import chunk_document
from app.knowledge.vector_store import add_chunks, get_stats


def ingest_documents() -> None:
    """Read all .md and .txt files from the docs directory and ingest them."""
    docs_dir = Path(settings.docs_path)

    if not docs_dir.exists():
        print(f"[ingest] ERROR: Docs directory not found: {docs_dir}")
        sys.exit(1)

    doc_files = sorted(
        list(docs_dir.glob("*.md")) + list(docs_dir.glob("*.txt"))
    )

    if not doc_files:
        print(f"[ingest] No .md or .txt files found in {docs_dir}")
        sys.exit(1)

    print(f"[ingest] Found {len(doc_files)} documents in {docs_dir}")
    print(f"[ingest] Chunk size: {settings.chunk_size}, overlap: {settings.chunk_overlap}")
    print()

    total_chunks = 0

    for filepath in doc_files:
        text = filepath.read_text(encoding="utf-8")
        source = filepath.name

        chunks = chunk_document(
            text=text,
            source=source,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        n_added = add_chunks(chunks)
        total_chunks += n_added
        print(f"  [+] {source}: {n_added} chunks ({len(text)} chars)")

    print()
    print(f"[ingest] Total chunks ingested: {total_chunks}")

    stats = get_stats()
    print(f"[ingest] Vector store stats: {stats}")
    print("[ingest] Done!")


if __name__ == "__main__":
    ingest_documents()
