from typing import TypedDict


class GraphState(TypedDict, total=False):
    query: str
    answer: str
    process: str
    claims: list[str]
    retrieved_docs: dict[str, list[str]]
    expert_analyses: list[dict]
    tool_results: dict[str, str]
    evidence: list[dict]
    verification_results: list[dict]
    scores: dict[str, int]
    final_score: float
    confidence: str
    decision: str
    output: dict
