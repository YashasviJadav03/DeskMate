"""
Evaluation script — runs test queries and checks routing accuracy,
tool-call accuracy, and answer quality.

Usage:
    cd backend
    python -m eval.run_eval
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add backend/ to path
_BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(_BACKEND_DIR))

from app.agents.orchestrator import process_query


def load_test_queries() -> list[dict]:
    """Load test queries from JSON file."""
    test_file = Path(__file__).resolve().parent / "test_queries.json"
    with open(test_file, "r", encoding="utf-8") as f:
        return json.load(f)


def run_eval() -> None:
    """Run evaluation on all test queries."""
    queries = load_test_queries()

    print("=" * 70)
    print("  DeskMate Evaluation Report")
    print("=" * 70)
    print(f"\n  Total test queries: {len(queries)}\n")

    route_correct = 0
    agent_correct = 0
    tool_correct = 0
    keyword_scores = []
    total_tool_queries = 0

    for i, test in enumerate(queries, 1):
        query = test["query"]
        print(f"  [{i:2d}] Query: \"{query}\"")

        try:
            response = process_query(query)

            # Check routing
            route_ok = response.trace.route == test["expected_route"]
            if route_ok:
                route_correct += 1

            # Check agent
            agent_ok = response.trace.agent == test["expected_agent"]
            if agent_ok:
                agent_correct += 1

            # Check tool (if expected)
            tool_ok = True
            if test["expected_tool"]:
                total_tool_queries += 1
                tool_ok = response.trace.tool_called == test["expected_tool"]
                if tool_ok:
                    tool_correct += 1

            # Check keywords in answer
            answer_lower = response.response.lower()
            keywords = test.get("expected_keywords", [])
            if keywords:
                found = sum(1 for kw in keywords if kw.lower() in answer_lower)
                kw_score = found / len(keywords)
                keyword_scores.append(kw_score)
            else:
                kw_score = 1.0
                keyword_scores.append(kw_score)

            status = "[PASS]" if (route_ok and agent_ok and tool_ok) else "[FAIL]"
            r_mark = "OK" if route_ok else "X"
            a_mark = "OK" if agent_ok else "X"
            t_mark = "OK" if tool_ok else "X"
            print(f"       {status} Route: {response.trace.route} ({r_mark})"
                  f" | Agent: {response.trace.agent} ({a_mark})"
                  f" | Tool: {response.trace.tool_called or 'None'} ({t_mark})"
                  f" | Keywords: {kw_score:.0%}")

        except Exception as e:
            print(f"       [ERR] ERROR: {e}")
            keyword_scores.append(0.0)

    # ── Summary ──────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print(f"  Routing Accuracy:    {route_correct}/{len(queries)} ({route_correct/len(queries):.0%})")
    print(f"  Agent Accuracy:      {agent_correct}/{len(queries)} ({agent_correct/len(queries):.0%})")
    if total_tool_queries > 0:
        print(f"  Tool-Call Accuracy:  {tool_correct}/{total_tool_queries} ({tool_correct/total_tool_queries:.0%})")
    avg_kw = sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0
    print(f"  Avg Keyword Score:   {avg_kw:.0%}")
    print("=" * 70)


if __name__ == "__main__":
    run_eval()
