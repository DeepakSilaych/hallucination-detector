from state import GraphState
from config import THRESHOLD_ACCEPT
from utils.output import format_output


def run(state: GraphState) -> dict:
    final_score = state.get("final_score", 0.0)

    decision = "accept" if final_score > THRESHOLD_ACCEPT else "fallback"

    output = format_output(
        final_score=final_score,
        confidence=state.get("confidence", "Unknown"),
        claims=state.get("claims", []),
        verification_results=state.get("verification_results", []),
    )
    return {"decision": decision, "output": output}
