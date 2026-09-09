"""
Router Agent — classifies incoming queries as 'informational' or 'actionable'.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.llm.base import BaseLLM


@dataclass
class RoutingResult:
    """Result of query classification."""
    route: str        # "informational" or "actionable"
    confidence: float
    reasoning: str = ""


CATEGORIES = ["informational", "actionable"]


class RouterAgent:
    """
    Classifies user queries to determine which downstream agent should handle them.

    - **informational**: Queries that need information from the knowledge base.
      Examples: "What is your return policy?", "How do I track my order?"

    - **actionable**: Queries that require performing an action (API call, tool use).
      Examples: "Check status of order #12345", "File a complaint about late delivery"
    """

    def __init__(self, llm: BaseLLM) -> None:
        self._llm = llm

    def classify(self, query: str) -> RoutingResult:
        """
        Classify a query into 'informational' or 'actionable'.

        Returns a RoutingResult with the classification, confidence, and reasoning.
        """
        category, confidence = self._llm.classify(query, CATEGORIES)

        # Ensure category is valid
        if category not in CATEGORIES:
            category = "informational"
            confidence = 0.3

        return RoutingResult(
            route=category,
            confidence=confidence,
            reasoning=f"Query classified as '{category}' with {confidence:.0%} confidence.",
        )
