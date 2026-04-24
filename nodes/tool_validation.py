import wikipedia

from state import GraphState


def _lookup_claim(claim: str) -> str:
    try:
        results = wikipedia.search(claim, results=2)
        if not results:
            return "No Wikipedia results found"
        return wikipedia.summary(results[0], sentences=3)
    except wikipedia.DisambiguationError as e:
        try:
            return wikipedia.summary(e.options[0], sentences=3)
        except Exception:
            return "Disambiguation error, could not resolve"
    except Exception:
        return "Validation unavailable"


def run(state: GraphState) -> dict:
    claims = state.get("claims", [])
    tool_results: dict[str, str] = {}
    for claim in claims:
        tool_results[claim] = _lookup_claim(claim)
    return {"tool_results": tool_results}
