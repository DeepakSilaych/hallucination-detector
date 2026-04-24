import json
import re

from state import GraphState
from utils.llm import get_llm
from prompts import CLAIM_DECOMPOSE


def _parse_claims(text: str) -> list[str]:
    cleaned = re.sub(r"```(?:json)?\s*", "", text).strip()
    json_match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if json_match:
        try:
            claims = json.loads(json_match.group())
            if isinstance(claims, list):
                return [str(c).strip() for c in claims if c]
        except json.JSONDecodeError:
            pass
    return [
        line.strip().lstrip("-•*0123456789.").strip()
        for line in cleaned.split("\n")
        if line.strip() and len(line.strip()) > 5
    ]


def run(state: GraphState) -> dict:
    llm = get_llm(temperature=0.0)
    response = llm.invoke(CLAIM_DECOMPOSE.format(
        query=state.get("query", ""),
        process=state.get("process", "No reasoning provided"),
        answer=state.get("answer", ""),
    ))
    return {"claims": _parse_claims(response.content)}
