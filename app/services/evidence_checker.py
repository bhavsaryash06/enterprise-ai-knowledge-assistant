def assess_evidence_strength(
    retrieved_chunks: list[dict],
    minimum_results: int = 1,
    medium_score_threshold: float = 0.55,
    high_score_threshold: float = 0.68,
) -> dict:
    if not retrieved_chunks:
        return {
            "confidence": "low",
            "escalation_required": True,
            "reason": "No relevant document chunks were retrieved.",
            "top_score": None,
            "evidence_count": 0,
        }

    valid_chunks = [
        chunk for chunk in retrieved_chunks
        if chunk.get("text") and chunk.get("score") is not None
    ]

    if len(valid_chunks) < minimum_results:
        return {
            "confidence": "low",
            "escalation_required": True,
            "reason": "Not enough usable evidence was found.",
            "top_score": None,
            "evidence_count": len(valid_chunks),
        }

    top_score = max(chunk["score"] for chunk in valid_chunks)

    if top_score >= high_score_threshold:
        return {
            "confidence": "high",
            "escalation_required": False,
            "reason": "Strong supporting evidence was found.",
            "top_score": top_score,
            "evidence_count": len(valid_chunks),
        }

    if top_score >= medium_score_threshold:
        return {
            "confidence": "medium",
            "escalation_required": False,
            "reason": "Moderate supporting evidence was found.",
            "top_score": top_score,
            "evidence_count": len(valid_chunks),
        }

    return {
        "confidence": "low",
        "escalation_required": True,
        "reason": "Retrieved evidence appears weak or only loosely related based on similarity score.",
        "top_score": top_score,
        "evidence_count": len(valid_chunks),
    }