def format_source_label(chunk: dict) -> str:
    document_name = chunk.get("document_name") or "Unknown Document"
    department = chunk.get("department") or "Unknown Department"
    version = chunk.get("version") or "Unknown Version"
    chunk_number = chunk.get("chunk_number") or "Unknown Chunk"
    score = chunk.get("score")
    rerank_score = chunk.get("rerank_score")

    if isinstance(score, float):
        score_text = f"{score:.3f}"
    else:
        score_text = "N/A"

    if isinstance(rerank_score, float):
        rerank_score_text = f"{rerank_score:.3f}"
    else:
        rerank_score_text = "N/A"

    return (
        f"{document_name}, "
        f"Department: {department}, "
        f"Version: {version}, "
        f"Chunk: {chunk_number}, "
        f"Vector Score: {score_text}, "
        f"Rerank Score: {rerank_score_text}"
    )


def build_citations(retrieved_chunks: list[dict]) -> list[dict]:
    citations = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        citations.append(
            {
                "source_number": index,
                "source_label": format_source_label(chunk),
                "chunk_id": chunk.get("chunk_id"),
                "document_name": chunk.get("document_name"),
                "department": chunk.get("department"),
                "version": chunk.get("version"),
                "chunk_number": chunk.get("chunk_number"),
                "score": chunk.get("score"),
                "rerank_score": chunk.get("rerank_score"),
                "text_preview": (chunk.get("text") or "")[:250],
            }
        )

    return citations