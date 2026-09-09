"""
Embedding generator — wraps sentence-transformers for local embedding.
"""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Load the embedding model once and cache it."""
    print(f"[embedder] Loading model: {settings.embedding_model} ...")
    model = SentenceTransformer(settings.embedding_model)
    print(f"[embedder] Model loaded. Dimension: {model.get_sentence_embedding_dimension()}")
    return model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.

    Returns a list of float vectors, one per input text.
    """
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Generate an embedding for a single query string."""
    return embed_texts([query])[0]


def get_embedding_dimension() -> int:
    """Return the dimensionality of the embedding model."""
    return _get_model().get_sentence_embedding_dimension()
