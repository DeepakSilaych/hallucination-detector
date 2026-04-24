def format_output(
    final_score: float,
    confidence: str,
    claims: list[str],
    verification_results: list[dict],
) -> dict:
    return {
        "hallucination_score": round(final_score, 4),
        "confidence": confidence,
        "verdict": [
            {"claim": r["claim"], "result": r["verdict"]}
            for r in verification_results
        ],
    }
