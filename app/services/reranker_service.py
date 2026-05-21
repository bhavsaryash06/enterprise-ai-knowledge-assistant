from app.core.logger import logger


RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker_model = None


def get_reranker_model():
    global _reranker_model

    if _reranker_model is not None:
        return _reranker_model

    try:
        from sentence_transformers import CrossEncoder

        _reranker_model = CrossEncoder(RERANKER_MODEL_NAME)
        return _reranker_model

    except ImportError:
        logger.warning(
            "sentence-transformers is not installed. Falling back to vector-score ordering."
        )
        return None


def fallback_rerank_chunks(
    retrieved_chunks: list[dict],
    top_k: int = 5,
) -> list[dict]:
    sorted_chunks = sorted(
        retrieved_chunks,
        key=lambda chunk: chunk.get("score", 0),
        reverse=True,
    )

    for chunk in sorted_chunks:
        chunk["rerank_score"] = None

    return sorted_chunks[:top_k]


def rerank_chunks(
    question: str,
    retrieved_chunks: list[dict],
    top_k: int = 5,
) -> list[dict]:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not retrieved_chunks:
        return []

    model = get_reranker_model()

    if model is None:
        return fallback_rerank_chunks(
            retrieved_chunks=retrieved_chunks,
            top_k=top_k,
        )

    valid_chunks = [
        chunk
        for chunk in retrieved_chunks
        if chunk.get("text")
    ]

    if not valid_chunks:
        return []

    pairs = [
        [question, chunk.get("text", "")]
        for chunk in valid_chunks
    ]

    rerank_scores = model.predict(pairs)

    reranked_chunks = []

    for chunk, rerank_score in zip(valid_chunks, rerank_scores):
        updated_chunk = chunk.copy()
        updated_chunk["rerank_score"] = float(rerank_score)
        reranked_chunks.append(updated_chunk)

    reranked_chunks.sort(
        key=lambda chunk: chunk.get("rerank_score", 0),
        reverse=True,
    )

    return reranked_chunks[:top_k]