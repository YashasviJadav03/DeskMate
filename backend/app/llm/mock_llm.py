"""
Mock LLM — keyword-based routing and template responses.

No API key required. Used during development and as a fallback.
"""

from __future__ import annotations

import json
import re

from app.llm.base import BaseLLM, LLMResponse


# ── Keyword banks for classification ────────────────────

_ACTIONABLE_KEYWORDS = [
    "order status", "track order", "check order", "where is my order",
    "cancel order", "cancel my order",
    "complaint", "file a complaint", "log a complaint", "report",
    "send email", "send confirmation", "confirm", "send me",
    "refund my", "return my", "exchange my",
    "update my address", "change my address",
    "reset password", "change password",
    "complaint about", "unhappy with", "not satisfied",
    "late delivery", "wrong item", "damaged",
    "order #", "ord-",
]

_INFORMATIONAL_KEYWORDS = [
    "what is", "how do", "how can", "how to", "tell me about",
    "explain", "policy", "faq", "do you", "can i", "is there",
    "what are", "guide", "size", "shipping", "warranty",
    "payment", "methods", "loyalty", "gift card", "privacy",
    "return policy", "refund process", "international",
    "account", "support", "contact",
]


class MockLLM(BaseLLM):
    """
    Rule-based mock LLM for development.

    - classify: uses keyword matching
    - generate: returns templated answers from retrieved context
    - function_call: uses regex to extract tool parameters from the query
    """

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
    ) -> LLMResponse:
        """Generate a response based on retrieved context in the prompt."""
        # Extract context if present (between <context> tags)
        context_match = re.search(
            r"<context>(.*?)</context>", prompt, re.DOTALL
        )
        # Also try looking for "Context:" block
        if not context_match:
            context_match = re.search(
                r"Context:\s*\n(.*?)(?:\nQuestion:|\nQuery:|\Z)",
                prompt,
                re.DOTALL,
            )

        if context_match:
            context = context_match.group(1).strip()
            # Return first ~500 chars of context as the "answer"
            answer = context[:500]
            if len(context) > 500:
                answer += "..."
            return LLMResponse(
                text=f"Based on our documentation: {answer}",
                tokens_used=len(prompt.split()) + len(answer.split()),
            )

        return LLMResponse(
            text="I'm sorry, I don't have enough information to answer that question. Could you please rephrase or ask about our products, shipping, returns, or account management?",
            tokens_used=len(prompt.split()) + 30,
        )

    def classify(
        self,
        query: str,
        categories: list[str],
    ) -> tuple[str, float]:
        """Classify query using keyword matching."""
        query_lower = query.lower().strip()

        actionable_score = sum(
            1 for kw in _ACTIONABLE_KEYWORDS if kw in query_lower
        )
        informational_score = sum(
            1 for kw in _INFORMATIONAL_KEYWORDS if kw in query_lower
        )

        if actionable_score > informational_score:
            return "actionable", min(0.5 + actionable_score * 0.15, 0.95)
        elif informational_score > 0:
            return "informational", min(0.5 + informational_score * 0.15, 0.95)
        else:
            # Default to informational for ambiguous queries
            return "informational", 0.4

    def function_call(
        self,
        prompt: str,
        tools: list[dict],
        system_prompt: str = "",
    ) -> LLMResponse:
        """Determine which tool to call using keyword/regex matching."""
        prompt_lower = prompt.lower()

        # ── Check for order status ───────────────────────
        order_match = re.search(
            r"(?:order\s*(?:#|number|id)?[:\s]*)?(?:ord-?)(\d+)",
            prompt_lower,
        )
        if not order_match:
            order_match = re.search(r"#(\d+)", prompt_lower)

        if order_match and any(
            kw in prompt_lower
            for kw in ["status", "track", "check", "where", "order"]
        ):
            order_id = f"ORD-{order_match.group(1)}"
            return LLMResponse(
                text="",
                tokens_used=len(prompt.split()) + 10,
                tool_call={
                    "name": "check_order_status",
                    "arguments": {"order_id": order_id},
                },
            )

        # ── Check for complaint ──────────────────────────
        if any(
            kw in prompt_lower
            for kw in ["complaint", "unhappy", "not satisfied", "report", "issue with", "problem with"]
        ):
            # Extract a subject from the query
            subject = "Customer Complaint"
            if "late delivery" in prompt_lower:
                subject = "Late Delivery"
            elif "wrong item" in prompt_lower:
                subject = "Wrong Item Received"
            elif "damaged" in prompt_lower:
                subject = "Damaged Product"
            elif "quality" in prompt_lower:
                subject = "Product Quality Issue"

            return LLMResponse(
                text="",
                tokens_used=len(prompt.split()) + 10,
                tool_call={
                    "name": "log_complaint",
                    "arguments": {
                        "subject": subject,
                        "description": prompt.strip(),
                    },
                },
            )

        if any(
            kw in prompt_lower
            for kw in ["send email", "send confirmation", "confirmation email", "email me", "send me an email", "email to"]
        ):
            email_match = re.search(
                r"[\w.+-]+@[\w-]+\.[\w.]+", prompt
            )
            to_email = email_match.group(0) if email_match else "customer@example.com"

            return LLMResponse(
                text="",
                tokens_used=len(prompt.split()) + 10,
                tool_call={
                    "name": "send_confirmation_email",
                    "arguments": {
                        "to": to_email,
                        "subject": "ShopEase Confirmation",
                        "body": f"Thank you for your request. We are processing: {prompt[:100]}",
                    },
                },
            )

        # ── No tool match → plain response ───────────────
        return LLMResponse(
            text="I understand you'd like to take an action, but I'm not sure which one. Could you clarify? I can help with: checking order status, filing a complaint, or sending a confirmation email.",
            tokens_used=len(prompt.split()) + 40,
        )
