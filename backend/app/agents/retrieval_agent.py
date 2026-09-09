"""
Retrieval Agent — answers informational queries using RAG (Retrieval-Augmented Generation).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.llm.base import BaseLLM
from app.knowledge.vector_store import query_similar


@dataclass
class RetrievalResult:
    """Result from the retrieval agent."""
    answer: str
    sources: list[str] = field(default_factory=list)
    tokens_used: int = 0


_SYSTEM_PROMPT = """You are a helpful customer support assistant for ShopEase, an e-commerce platform.
Answer the user's question based ONLY on the provided context from our knowledge base.
If the context doesn't contain the answer, say so honestly.
Be concise, friendly, and professional. Use bullet points for clarity when listing steps."""


class RetrievalAgent:
    """
    RAG-based agent that:
    1. Queries the vector store for relevant document chunks.
    2. Constructs a prompt with retrieved context.
    3. Generates a grounded answer via the LLM.
    """

    def __init__(self, llm: BaseLLM, top_k: int = 5) -> None:
        self._llm = llm
        self._top_k = top_k

    def answer(self, query: str) -> RetrievalResult:
        """
        Answer an informational query using retrieval-augmented generation.
        """
        # ── 1. Retrieve relevant chunks ──────────────────
        results = query_similar(query, top_k=self._top_k)

        if not results:
            return RetrievalResult(
                answer="I'm sorry, I couldn't find any relevant information in our knowledge base. Please try rephrasing your question or contact our support team.",
                sources=[],
                tokens_used=0,
            )

        # ── 2. Build context block ───────────────────────
        context_parts = []
        sources = set()
        for r in results:
            context_parts.append(r["text"])
            sources.add(r["source"])

        context = "\n\n---\n\n".join(context_parts)

        # ── 3. Build prompt ──────────────────────────────
        prompt = (
            f"<context>\n{context}\n</context>\n\n"
            f"Question: {query}\n\n"
            f"Answer the question based on the context above."
        )

        # ── 4. Generate answer ───────────────────────────
        response = self._llm.generate(
            prompt=prompt,
            system_prompt=_SYSTEM_PROMPT,
            temperature=0.3,
        )

        return RetrievalResult(
            answer=response.text,
            sources=sorted(sources),
            tokens_used=response.tokens_used,
        )
