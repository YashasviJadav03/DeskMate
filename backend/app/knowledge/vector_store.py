"""
Vector store — ChromaDB interface for storing and querying document chunks.
"""

from __future__ import annotations

import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.knowledge.chunker import Chunk
from app.knowledge.embedder import embed_texts, embed_query


_COLLECTION_NAME = "deskmate_docs"


from functools import lru_cache


@lru_cache(maxsize=1)
def _get_client() -> chromadb.ClientAPI:
    """Create a persistent ChromaDB client (cached)."""
    return chromadb.PersistentClient(
        path=settings.chroma_db_path,
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )


def _is_legacy_chroma() -> bool:
    """Check if we're on an older ChromaDB that uses the Settings-based API."""
    try:
        chromadb.PersistentClient
        return False
    except AttributeError:
        return True


def get_collection() -> chromadb.Collection:
    """Get or create the document collection."""
    client = _get_client()
    return client.get_or_create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(chunks: list[Chunk]) -> int:
    """
    Add document chunks to the vector store.

    Returns the number of chunks added.
    """
    if not chunks:
        return 0

    collection = get_collection()

    # Prepare batch data
    ids = [chunk.id for chunk in chunks]
    documents = [chunk.text for chunk in chunks]
    metadatas = [
        {
            "source": chunk.source,
            "chunk_index": chunk.chunk_index,
            **chunk.metadata,
        }
        for chunk in chunks
    ]

    # Generate embeddings
    embeddings = embed_texts(documents)

    # Upsert (idempotent — safe to re-run)
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def query_similar(
    query: str,
    top_k: Optional[int] = None,
) -> list[dict]:
    """
    Find the top-k most similar chunks to a query.

    Returns a list of dicts with keys: text, source, score, metadata.
    """
    k = top_k or settings.retrieval_top_k
    collection = get_collection()

    # Check if collection has documents
    if collection.count() == 0:
        return []

    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    # Unpack results (ChromaDB returns nested lists)
    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append(
            {
                "text": doc,
                "source": meta.get("source", "unknown"),
                "score": 1 - dist,  # cosine distance → similarity
                "metadata": meta,
            }
        )

    return output


def get_stats() -> dict:
    """Return basic stats about the vector store."""
    collection = get_collection()
    return {
        "collection_name": _COLLECTION_NAME,
        "total_chunks": collection.count(),
    }
