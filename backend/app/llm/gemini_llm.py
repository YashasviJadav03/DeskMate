"""
Gemini LLM — Google Generative AI integration.

Requires GEMINI_API_KEY in .env.
"""

from __future__ import annotations

import json
from typing import Any

import google.generativeai as genai

from app.config import settings
from app.llm.base import BaseLLM, LLMResponse


class GeminiLLM(BaseLLM):
    """Gemini API-based LLM provider."""

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Set it in .env or use LLM_PROVIDER=mock for development."
            )
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(settings.gemini_model)

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
    ) -> LLMResponse:
        """Generate text using Gemini."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        response = self._model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=1024,
            ),
        )

        text = response.text if response.text else ""
        tokens = (
            response.usage_metadata.total_token_count
            if hasattr(response, "usage_metadata") and response.usage_metadata
            else len(prompt.split()) + len(text.split())
        )

        return LLMResponse(text=text, tokens_used=tokens)

    def classify(
        self,
        query: str,
        categories: list[str],
    ) -> tuple[str, float]:
        """Classify a query using Gemini."""
        categories_str = ", ".join(categories)
        prompt = (
            f"Classify the following customer query into exactly one of these categories: {categories_str}.\n\n"
            f"Query: \"{query}\"\n\n"
            f"Respond with ONLY a JSON object: {{\"category\": \"<category>\", \"confidence\": <0.0-1.0>}}"
        )

        response = self.generate(prompt, temperature=0.1)

        try:
            result = json.loads(response.text.strip().strip("`").replace("json\n", ""))
            return result["category"], result["confidence"]
        except (json.JSONDecodeError, KeyError):
            # Fallback: check if any category name appears in the response
            text_lower = response.text.lower()
            for cat in categories:
                if cat.lower() in text_lower:
                    return cat, 0.6
            return categories[0], 0.3

    def function_call(
        self,
        prompt: str,
        tools: list[dict],
        system_prompt: str = "",
    ) -> LLMResponse:
        """Use Gemini to decide which tool to call."""
        tools_desc = json.dumps(tools, indent=2)
        full_prompt = (
            f"{system_prompt}\n\n" if system_prompt else ""
        ) + (
            f"You have access to the following tools:\n{tools_desc}\n\n"
            f"User query: \"{prompt}\"\n\n"
            f"If a tool should be called, respond with ONLY a JSON object:\n"
            f"{{\"tool_call\": {{\"name\": \"<tool_name>\", \"arguments\": {{...}}}}}}\n\n"
            f"If no tool is needed, respond with a helpful text answer.\n"
            f"Respond:"
        )

        response = self.generate(full_prompt, temperature=0.1)
        text = response.text.strip()

        # Try to parse as tool call
        try:
            clean = text.strip("`").replace("json\n", "")
            parsed = json.loads(clean)
            if "tool_call" in parsed:
                return LLMResponse(
                    text="",
                    tokens_used=response.tokens_used,
                    tool_call=parsed["tool_call"],
                )
        except (json.JSONDecodeError, KeyError):
            pass

        return LLMResponse(text=text, tokens_used=response.tokens_used)
