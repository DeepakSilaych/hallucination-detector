from langgraph.graph import StateGraph, END
from state import GraphState
from nodes import (
    claim_decomposer,
    retrieval,
    expert_analysis,
    tool_validation,
    evidence_aggregator,
    verifier,
    scoring,
    routing,
    fallback,
)


def _fan_out(_state: GraphState) -> list[str]:
    return ["retrieval", "expert_analysis", "tool_validation"]


def _route_decision(state: GraphState) -> str:
    return state["decision"]


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("claim_decomposer", claim_decomposer.run)
    builder.add_node("retrieval", retrieval.run)
    builder.add_node("expert_analysis", expert_analysis.run)
    builder.add_node("tool_validation", tool_validation.run)
    builder.add_node("evidence_aggregator", evidence_aggregator.run)
    builder.add_node("verifier", verifier.run)
    builder.add_node("scoring", scoring.run)
    builder.add_node("routing", routing.run)
    builder.add_node("fallback", fallback.run)

    builder.set_entry_point("claim_decomposer")

    builder.add_conditional_edges("claim_decomposer", _fan_out)

    builder.add_edge("retrieval", "evidence_aggregator")
    builder.add_edge("expert_analysis", "evidence_aggregator")
    builder.add_edge("tool_validation", "evidence_aggregator")

    builder.add_edge("evidence_aggregator", "verifier")
    builder.add_edge("verifier", "scoring")
    builder.add_edge("scoring", "routing")

    builder.add_conditional_edges(
        "routing",
        _route_decision,
        {"accept": END, "fallback": "fallback"},
    )

    builder.add_edge("fallback", END)

    return builder.compile()
