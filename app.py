import json
from pathlib import Path
from typing import Any, Iterable

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from graph import build_graph
from prompts import AGENT_PLAN, AGENT_REASON, AGENT_ANSWER
from utils.llm import get_llm
from knowledge.store import search as kb_search

APP_DIR = Path(__file__).resolve().parent
WEB_DIR = APP_DIR / "web"
WEB_INDEX = WEB_DIR / "index.html"

app = FastAPI(title="Hallucination Detector")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

_graph = None

STATE_KEYS = [
    "claims",
    "retrieved_docs",
    "expert_analyses",
    "tool_results",
    "evidence",
    "verification_results",
    "scores",
    "final_score",
    "confidence",
    "decision",
    "output",
]

NODE_ORDER = [
    "claim_decomposer",
    "retrieval",
    "expert_analysis",
    "tool_validation",
    "evidence_aggregator",
    "verifier",
    "scoring",
    "routing",
    "fallback",
]


def _get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


class GenerateRequest(BaseModel):
    query: str = Field(..., min_length=1)


class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    process: str | None = None


def _select_state(state: dict[str, Any]) -> dict[str, Any]:
    return {key: state.get(key) for key in STATE_KEYS}


def _sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.get("/")
def serve_index() -> FileResponse:
    if not WEB_INDEX.exists():
        raise HTTPException(status_code=404, detail="Index file not found")
    return FileResponse(WEB_INDEX)


def _run_agent_pipeline(query: str) -> dict[str, str]:
    import re
    llm = get_llm(temperature=0.3, weak=True)
    steps: list[str] = []

    plan_response = llm.invoke(AGENT_PLAN.format(query=query))
    plan_text = re.sub(r"```(?:json)?\s*", "", plan_response.content).strip().removesuffix("```").strip()
    try:
        sub_queries = json.loads(plan_text)
        if not isinstance(sub_queries, list):
            sub_queries = [query]
    except json.JSONDecodeError:
        sub_queries = [query]
    steps.append(f"[Plan] Identified sub-queries: {sub_queries}")

    all_results: list[str] = []
    for sq in sub_queries:
        docs = kb_search(sq, k=2)
        steps.append(f"[Search] '{sq}' → {len(docs)} results:")
        for doc in docs:
            steps.append(f"  - {doc[:200]}")
        all_results.extend(docs)

    search_block = "\n---\n".join(all_results) if all_results else "No relevant documents found."

    reason_response = llm.invoke(AGENT_REASON.format(
        query=query, search_results=search_block,
    ))
    reasoning = reason_response.content.strip()
    steps.append(f"[Reason] {reasoning}")

    answer_response = llm.invoke(AGENT_ANSWER.format(
        query=query, reasoning=reasoning,
    ))
    answer = answer_response.content.strip()

    process = "\n\n".join(steps)
    return {"answer": answer, "process": process}


@app.post("/api/generate")
def generate(payload: GenerateRequest) -> dict[str, str]:
    try:
        return _run_agent_pipeline(payload.query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/analyze")
def analyze(payload: AnalyzeRequest) -> dict[str, Any]:
    graph = _get_graph()
    state = {
        "query": payload.query,
        "answer": payload.answer,
        "process": payload.process or "",
    }
    try:
        result = graph.invoke(state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return _select_state(result)


@app.post("/api/stream")
def stream(payload: AnalyzeRequest) -> StreamingResponse:
    graph = _get_graph()
    state = {
        "query": payload.query,
        "answer": payload.answer,
        "process": payload.process or "",
    }

    def event_stream() -> Iterable[str]:
        local_state = dict(state)
        yield _sse("meta", {"nodes": NODE_ORDER})
        yield _sse("status", {"status": "started"})
        try:
            for update in graph.stream(state, stream_mode="updates"):
                if not update:
                    continue
                for node, node_update in update.items():
                    if isinstance(node_update, dict):
                        local_state.update(node_update)
                    yield _sse(
                        "node",
                        {
                            "node": node,
                            "status": "completed",
                            "update": node_update,
                            "state": _select_state(local_state),
                        },
                    )
            yield _sse("done", {"state": _select_state(local_state)})
        except Exception as exc:
            yield _sse("error", {"message": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
