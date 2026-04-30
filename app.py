import json
from pathlib import Path
from typing import Any, Iterable

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from graph import build_graph

APP_DIR = Path(__file__).resolve().parent
WEB_INDEX = APP_DIR / "web" / "index.html"

app = FastAPI(title="Hallucination Detector")

_graph = None

STATE_KEYS = [
    "claims",
    "retrieved_docs",
    "consistency_answers",
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
    "self_consistency",
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
