from state import GraphState
from utils.llm import get_llm
from prompts import VERIFY_CLAIM


def _normalize_verdict(text: str) -> str:
    lower = text.strip().lower()
    if "support" in lower:
        return "Supported"
    if "contradict" in lower:
        return "Contradicted"
    return "Not Enough Info"


def run(state: GraphState) -> dict:
    evidence_list = state.get("evidence", [])
    llm = get_llm(temperature=0.0)

    results = []
    for item in evidence_list:
        retrieval_text = "\n".join(item.get("retrieval", []))
        expert_entries = item.get("expert_analyses", [])
        consistency_text = "\n---\n".join(
            f"[{e.get('persona', 'Expert')}]: {e.get('answer', '')}"
            for e in expert_entries
        )
        tool_text = item.get("tool", "No data available")

        prompt = VERIFY_CLAIM.format(
            claim=item["claim"],
            retrieval_evidence=retrieval_text or "No retrieval evidence available",
            consistency_evidence=consistency_text or "No consistency evidence available",
            tool_evidence=tool_text,
        )
        response = llm.invoke(prompt)
        results.append({
            "claim": item["claim"],
            "verdict": _normalize_verdict(response.content),
        })
    return {"verification_results": results}
