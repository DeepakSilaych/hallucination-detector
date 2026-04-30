from state import GraphState


def run(state: GraphState) -> dict:
    claims = state.get("claims", [])
    retrieved_docs = state.get("retrieved_docs", {})
    expert_analyses = state.get("expert_analyses", [])
    tool_results = state.get("tool_results", {})

    evidence = []
    for claim in claims:
        evidence.append({
            "claim": claim,
            "retrieval": retrieved_docs.get(claim, []),
            "expert_analyses": expert_analyses,
            "tool": tool_results.get(claim, "No data available"),
        })
    return {"evidence": evidence}
