from state import GraphState
from config import SCORE_SUPPORTED, SCORE_CONTRADICTED, SCORE_UNKNOWN, THRESHOLD_ACCEPT


def _compute_confidence(score: float) -> str:
    if score > THRESHOLD_ACCEPT:
        return "Reliable"
    if score > 0:
        return "Uncertain"
    return "Likely Hallucinated"


def run(state: GraphState) -> dict:
    results = state.get("verification_results", [])

    counts = {"Supported": 0, "Contradicted": 0, "Not Enough Info": 0}
    for r in results:
        verdict = r.get("verdict", "Not Enough Info")
        counts[verdict] = counts.get(verdict, 0) + 1

    total = len(results) or 1
    raw_score = (
        counts["Supported"] * SCORE_SUPPORTED
        + counts["Contradicted"] * SCORE_CONTRADICTED
        + counts["Not Enough Info"] * SCORE_UNKNOWN
    )
    final_score = raw_score / total

    return {
        "scores": counts,
        "final_score": final_score,
        "confidence": _compute_confidence(final_score),
    }
