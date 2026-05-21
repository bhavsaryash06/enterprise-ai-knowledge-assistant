from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=10)
    use_query_rewrite: bool = True
    use_reranking: bool = True
    department: str | None = None
    document_type: str | None = None


class RetrievedChunkResponse(BaseModel):
    score: float
    rerank_score: float | None = None
    chunk_id: str | None = None
    document_id: str | None = None
    document_name: str | None = None
    department: str | None = None
    document_type: str | None = None
    version: str | None = None
    chunk_number: int | None = None
    text: str | None = None
    source_path: str | None = None


class RetrievalResponse(BaseModel):
    question: str
    rewritten_query: str | None = None
    total_results: int
    retrieved_chunks: list[RetrievedChunkResponse]


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=10)
    use_query_rewrite: bool = True
    use_reranking: bool = True
    department: str | None = None
    document_type: str | None = None


class SourceResponse(BaseModel):
    source_number: int | None = None
    source_label: str | None = None
    chunk_id: str | None = None
    document_name: str | None = None
    department: str | None = None
    version: str | None = None
    chunk_number: int | None = None
    score: float | None = None
    rerank_score: float | None = None
    text_preview: str | None = None


class AskResponse(BaseModel):
    question: str
    rewritten_query: str | None = None
    answer: str
    confidence: str
    escalation_required: bool
    evidence_reason: str | None = None
    top_score: float | None = None
    sources: list[SourceResponse]
    retrieved_chunks: list[RetrievedChunkResponse]