"""
Abstract base class for LLM providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    """Unified response from any LLM provider."""

    text: str
    tokens_used: int = 0
    tool_call: dict | None = None  # {"name": ..., "arguments": {...}}
    raw: dict = field(default_factory=dict)


class BaseLLM(ABC):
    """Interface that all LLM implementations must follow."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
    ) -> LLMResponse:
        """Generate a text response given a prompt."""
        ...

    @abstractmethod
    def classify(
        self,
        query: str,
        categories: list[str],
    ) -> tuple[str, float]:
        """
        Classify a query into one of the given categories.

        Returns (category, confidence).
        """
        ...

    @abstractmethod
    def function_call(
        self,
        prompt: str,
        tools: list[dict],
        system_prompt: str = "",
    ) -> LLMResponse:
        """
        Generate a response that may include a tool/function call.

        *tools* is a list of JSON-schema tool definitions.
        If the LLM decides to call a tool, response.tool_call will be populated.
        """
        ...
