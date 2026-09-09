"""
Action Agent — handles actionable queries using tool/function calling.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from app.llm.base import BaseLLM
from app.tools.order_status import (
    check_order_status,
    TOOL_SCHEMA as ORDER_SCHEMA,
)
from app.tools.complaint import (
    log_complaint,
    TOOL_SCHEMA as COMPLAINT_SCHEMA,
)
from app.tools.email_sender import (
    send_confirmation_email,
    TOOL_SCHEMA as EMAIL_SCHEMA,
)


@dataclass
class ActionResult:
    """Result from the action agent."""
    answer: str
    tool_called: str | None = None
    tool_input: dict | None = None
    tool_output: dict | None = None
    tokens_used: int = 0


# ── Tool registry ────────────────────────────────────────

_TOOL_SCHEMAS = [ORDER_SCHEMA, COMPLAINT_SCHEMA, EMAIL_SCHEMA]

_TOOL_FUNCTIONS: dict[str, Callable[..., dict]] = {
    "check_order_status": check_order_status,
    "log_complaint": log_complaint,
    "send_confirmation_email": send_confirmation_email,
}


_SYSTEM_PROMPT = """You are a helpful customer support assistant for ShopEase.
You can perform actions on behalf of customers using the available tools.
Always confirm what action you're taking and provide the result clearly."""


class ActionAgent:
    """
    Tool-calling agent that:
    1. Uses the LLM to decide which tool to call.
    2. Executes the tool with extracted parameters.
    3. Formats the result into a user-friendly response.
    """

    def __init__(self, llm: BaseLLM) -> None:
        self._llm = llm

    def execute(self, query: str) -> ActionResult:
        """
        Handle an actionable query by calling the appropriate tool.
        """
        # ── 1. Ask LLM which tool to call ────────────────
        response = self._llm.function_call(
            prompt=query,
            tools=_TOOL_SCHEMAS,
            system_prompt=_SYSTEM_PROMPT,
        )

        # ── 2. If no tool call, return LLM's text ───────
        if response.tool_call is None:
            return ActionResult(
                answer=response.text,
                tokens_used=response.tokens_used,
            )

        tool_name = response.tool_call["name"]
        tool_args = response.tool_call.get("arguments", {})

        # ── 3. Validate tool exists ──────────────────────
        if tool_name not in _TOOL_FUNCTIONS:
            return ActionResult(
                answer=f"I'm sorry, I don't have access to a tool called '{tool_name}'. I can help with: checking order status, filing complaints, or sending confirmation emails.",
                tool_called=tool_name,
                tool_input=tool_args,
                tokens_used=response.tokens_used,
            )

        # ── 4. Execute the tool ──────────────────────────
        try:
            tool_fn = _TOOL_FUNCTIONS[tool_name]
            result = tool_fn(**tool_args)
        except TypeError as e:
            return ActionResult(
                answer=f"I couldn't execute that action due to missing or invalid parameters: {e}. Could you please provide more details?",
                tool_called=tool_name,
                tool_input=tool_args,
                tokens_used=response.tokens_used,
            )
        except Exception as e:
            return ActionResult(
                answer=f"I encountered an error while processing your request: {e}. Please try again or contact our support team.",
                tool_called=tool_name,
                tool_input=tool_args,
                tokens_used=response.tokens_used,
            )

        # ── 5. Format the result ─────────────────────────
        answer = self._format_tool_result(tool_name, tool_args, result)

        return ActionResult(
            answer=answer,
            tool_called=tool_name,
            tool_input=tool_args,
            tool_output=result,
            tokens_used=response.tokens_used,
        )

    def _format_tool_result(
        self, tool_name: str, tool_args: dict, result: dict
    ) -> str:
        """Format tool results into a user-friendly response."""
        if not result.get("success", False):
            error = result.get("error", "An unknown error occurred.")
            return f"I'm sorry, there was an issue: {error}"

        if tool_name == "check_order_status":
            order = result
            lines = [
                f"📦 **Order {order['order_id']}**",
                f"• **Status**: {order['status']}",
                f"• **Items**: {', '.join(order.get('items', []))}",
                f"• **Total**: ${order.get('total', 0):.2f}",
                f"• **Ordered**: {order.get('ordered_date', 'N/A')}",
                f"• **Estimated Delivery**: {order.get('estimated_delivery', 'N/A')}",
            ]
            if order.get("tracking_number"):
                lines.append(f"• **Tracking**: {order['tracking_number']} ({order.get('carrier', 'N/A')})")
            return "\n".join(lines)

        elif tool_name == "log_complaint":
            return (
                f"✅ {result['message']}\n\n"
                f"• **Ticket ID**: {result['ticket_id']}\n"
                f"• **Subject**: {result['subject']}\n"
                f"• **Priority**: {result['priority']}\n"
                f"• **Status**: {result['status']}"
            )

        elif tool_name == "send_confirmation_email":
            return f"✅ {result['message']}"

        # Generic fallback
        return f"Action completed successfully: {json.dumps(result, indent=2)}"
