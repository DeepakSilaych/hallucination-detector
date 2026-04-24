from state import GraphState
from knowledge.store import search
from config import RETRIEVAL_TOP_K


def run(state: GraphState) -> dict:
    claims = state.get("claims", [])
    retrieved_docs: dict[str, list[str]] = {}
    for claim in claims:
        retrieved_docs[claim] = search(claim, k=RETRIEVAL_TOP_K)
    return {"retrieved_docs": retrieved_docs}
