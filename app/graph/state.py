from typing import Any, TypedDict


class RAGState(TypedDict, total=False):
    question: str
    top_k: int
    use_query_rewrite: bool
    use_reranking: bool
    department: str | None
    document_type: str | None

    rewritten_query: str | None
    retrieval_query: str | None
    retrieved_chunks: list[dict[str, Any]]

    answer: str
    confidence: str
    escalation_required: bool
    evidence_reason: str | None
    top_score: float | None
    sources: list[dict[str, Any]]

    error: str | None