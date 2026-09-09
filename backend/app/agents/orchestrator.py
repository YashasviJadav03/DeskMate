"""
Orchestrator — LangGraph state graph that wires Router, Retrieval, and Action agents.

Graph flow:
    START → classify → (informational) → retrieve → respond → END
                     → (actionable)   → act      → respond → END
"""

from __future__ import annotations

import time
import uuid
from typing import Any, TypedDict

from langgraph.graph import StateGraph, END

from app.config import settings
from app.llm.base import BaseLLM
from app.llm.mock_llm import MockLLM
from app.agents.router_agent import RouterAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.action_agent import ActionAgent
from app.models import ChatResponse, AgentTrace


# ── State schema ─────────────────────────────────────────


class AgentState(TypedDict):
    """State passed between graph nodes."""
    query: str
    session_id: str
    route: str
    confidence: float
    agent: str
    answer: str
    tool_called: str | None
    tool_input: dict | None
    tool_output: dict | None
    sources: list[str] | None
    tokens_used: int
    start_time: float


# ── LLM factory ──────────────────────────────────────────


def _create_llm() -> BaseLLM:
    """Create the appropriate LLM based on config."""
    if settings.llm_provider == "gemini":
        from app.llm.gemini_llm import GeminiLLM
        return GeminiLLM()
    return MockLLM()


# ── Graph node functions ─────────────────────────────────

# Shared agent instances (lazy-initialized)
_llm: BaseLLM | None = None
_router: RouterAgent | None = None
_retriever: RetrievalAgent | None = None
_actor: ActionAgent | None = None


def _get_agents() -> tuple[RouterAgent, RetrievalAgent, ActionAgent]:
    """Lazy-initialize agents."""
    global _llm, _router, _retriever, _actor
    if _llm is None:
        _llm = _create_llm()
        _router = RouterAgent(_llm)
        _retriever = RetrievalAgent(_llm, top_k=settings.retrieval_top_k)
        _actor = ActionAgent(_llm)
    return _router, _retriever, _actor


def classify_node(state: AgentState) -> dict:
    """Router Agent: classify the query."""
    router, _, _ = _get_agents()
    result = router.classify(state["query"])
    return {
        "route": result.route,
        "confidence": result.confidence,
    }


def retrieve_node(state: AgentState) -> dict:
    """Retrieval Agent: answer informational queries via RAG."""
    _, retriever, _ = _get_agents()
    result = retriever.answer(state["query"])
    return {
        "agent": "retrieval_agent",
        "answer": result.answer,
        "sources": result.sources,
        "tokens_used": result.tokens_used,
    }


def act_node(state: AgentState) -> dict:
    """Action Agent: handle actionable queries with tools."""
    _, _, actor = _get_agents()
    result = actor.execute(state["query"])
    return {
        "agent": "action_agent",
        "answer": result.answer,
        "tool_called": result.tool_called,
        "tool_input": result.tool_input,
        "tool_output": result.tool_output,
        "tokens_used": result.tokens_used,
    }


def respond_node(state: AgentState) -> dict:
    """Final response formatting."""
    return {"answer": state.get("answer", "")}


# ── Routing function ─────────────────────────────────────


def route_query(state: AgentState) -> str:
    """Conditional edge: decide which agent to invoke."""
    if state["route"] == "actionable":
        return "act"
    return "retrieve"


# ── Build the graph ──────────────────────────────────────


def build_graph() -> StateGraph:
    """Construct and compile the LangGraph state graph."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("classify", classify_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("act", act_node)
    graph.add_node("respond", respond_node)

    # Set entry point
    graph.set_entry_point("classify")

    # Conditional routing after classification
    graph.add_conditional_edges(
        "classify",
        route_query,
        {
            "retrieve": "retrieve",
            "act": "act",
        },
    )

    # Both agents flow to respond
    graph.add_edge("retrieve", "respond")
    graph.add_edge("act", "respond")

    # Respond → END
    graph.add_edge("respond", END)

    return graph.compile()


# ── Compiled graph singleton ─────────────────────────────

_compiled_graph = None


def get_graph():
    """Get the compiled graph (singleton)."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


# ── Public API ───────────────────────────────────────────


def process_query(query: str, session_id: str | None = None) -> ChatResponse:
    """
    Process a user query through the full agent pipeline.

    Returns a ChatResponse with the answer and agent trace.
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    start_time = time.time()

    # Initial state
    initial_state: AgentState = {
        "query": query,
        "session_id": session_id,
        "route": "",
        "confidence": 0.0,
        "agent": "",
        "answer": "",
        "tool_called": None,
        "tool_input": None,
        "tool_output": None,
        "sources": None,
        "tokens_used": 0,
        "start_time": start_time,
    }

    # Run the graph
    graph = get_graph()
    final_state = graph.invoke(initial_state)

    latency_ms = (time.time() - start_time) * 1000

    return ChatResponse(
        response=final_state["answer"],
        trace=AgentTrace(
            route=final_state["route"],
            agent=final_state.get("agent", "unknown"),
            tool_called=final_state.get("tool_called"),
            tool_input=final_state.get("tool_input"),
            tool_output=final_state.get("tool_output"),
            sources=final_state.get("sources"),
            latency_ms=round(latency_ms, 2),
        ),
        session_id=session_id,
    )
