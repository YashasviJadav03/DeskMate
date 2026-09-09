"""
Document chunker — splits markdown/text documents into overlapping chunks
for embedding and storage in the vector database.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Chunk:
    """A single text chunk from a document."""

    text: str
    source: str  # filename / document ID
    chunk_index: int
    metadata: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        """Unique ID for this chunk (used as ChromaDB document ID)."""
        return f"{self.source}::chunk-{self.chunk_index}"


def chunk_document(
    text: str,
    source: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[Chunk]:
    """
    Split a document into chunks using paragraph-based splitting with
    a character-size fallback.

    Strategy:
    1. Split on double-newlines (paragraphs / markdown sections).
    2. Merge small consecutive paragraphs into chunks up to *chunk_size* chars.
    3. If a single paragraph exceeds *chunk_size*, hard-split it on sentence
       boundaries (or word boundaries as a last resort).
    4. Add *chunk_overlap* characters of trailing context from the previous
       chunk to the start of the next chunk for retrieval continuity.
    """
    # ── 1. Split into paragraphs ─────────────────────────
    paragraphs = _split_paragraphs(text)

    # ── 2. Merge small paragraphs → raw chunks ──────────
    raw_chunks: list[str] = []
    buffer = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph would exceed the limit, flush the buffer
        if buffer and len(buffer) + len(para) + 2 > chunk_size:
            raw_chunks.append(buffer.strip())
            buffer = ""

        # If a single paragraph is too large, split it further
        if len(para) > chunk_size:
            if buffer:
                raw_chunks.append(buffer.strip())
                buffer = ""
            for sub in _split_large_paragraph(para, chunk_size):
                raw_chunks.append(sub.strip())
        else:
            buffer = f"{buffer}\n\n{para}" if buffer else para

    if buffer.strip():
        raw_chunks.append(buffer.strip())

    # ── 3. Apply overlap ────────────────────────────────
    chunks: list[Chunk] = []
    for i, raw in enumerate(raw_chunks):
        if i > 0 and chunk_overlap > 0:
            prev_tail = raw_chunks[i - 1][-chunk_overlap:]
            raw = f"...{prev_tail} {raw}"

        chunks.append(
            Chunk(
                text=raw,
                source=source,
                chunk_index=i,
                metadata={"char_count": len(raw)},
            )
        )

    return chunks


# ── Helpers ──────────────────────────────────────────────


def _split_paragraphs(text: str) -> list[str]:
    """Split text on double newlines (markdown paragraph boundaries)."""
    # Also treat markdown headers as split points
    text = re.sub(r"\n(#{1,6}\s)", r"\n\n\1", text)
    return re.split(r"\n\s*\n", text)


def _split_large_paragraph(text: str, max_size: int) -> list[str]:
    """Split an oversized paragraph on sentence boundaries, then word boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    parts: list[str] = []
    buffer = ""

    for sentence in sentences:
        if buffer and len(buffer) + len(sentence) + 1 > max_size:
            parts.append(buffer.strip())
            buffer = ""

        if len(sentence) > max_size:
            # Last resort: split on words
            words = sentence.split()
            for word in words:
                if buffer and len(buffer) + len(word) + 1 > max_size:
                    parts.append(buffer.strip())
                    buffer = ""
                buffer = f"{buffer} {word}" if buffer else word
        else:
            buffer = f"{buffer} {sentence}" if buffer else sentence

    if buffer.strip():
        parts.append(buffer.strip())

    return parts
