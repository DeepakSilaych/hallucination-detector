from state import GraphState
from utils.output import format_output


def run(state: GraphState) -> dict:
    output = format_output(
        final_score=state.get("final_score", 0.0),
        confidence="Likely Hallucinated",
        claims=state.get("claims", []),
        verification_results=state.get("verification_results", []),
    )
    return {"output": output}
