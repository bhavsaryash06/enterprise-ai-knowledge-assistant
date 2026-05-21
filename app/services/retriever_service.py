from typing import Any

from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.core.config import settings
from app.services.embedding_service import create_embedding
from app.services.qdrant_service import get_qdrant_client


def build_metadata_filter(
    department: str | None = None,
    document_type: str | None = None,
) -> Filter | None:
    filter_conditions = []

    if department:
        filter_conditions.append(
            FieldCondition(
                key="department",
                match=MatchValue(value=department),
            )
        )

    if document_type:
        filter_conditions.append(
            FieldCondition(
                key="document_type",
                match=MatchValue(value=document_type),
            )
        )

    if not filter_conditions:
        return None

    return Filter(must=filter_conditions)


def retrieve_relevant_chunks(
    query: str,
    top_k: int = 5,
    score_threshold: float | None = None,
    department: str | None = None,
    document_type: str | None = None,
) -> list[dict[str, Any]]:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    query_embedding = create_embedding(query)

    client = get_qdrant_client()

    metadata_filter = build_metadata_filter(
        department=department,
        document_type=document_type,
    )

    search_response = client.query_points(
        collection_name=settings.qdrant_collection_name,
        query=query_embedding,
        query_filter=metadata_filter,
        limit=top_k,
        with_payload=True,
    )

    retrieved_chunks = []

    for point in search_response.points:
        if score_threshold is not None and point.score < score_threshold:
            continue

        payload = point.payload or {}

        retrieved_chunks.append(
            {
                "score": point.score,
                "chunk_id": payload.get("chunk_id"),
                "document_id": payload.get("document_id"),
                "document_name": payload.get("document_name"),
                "department": payload.get("department"),
                "document_type": payload.get("document_type"),
                "version": payload.get("version"),
                "chunk_number": payload.get("chunk_number"),
                "text": payload.get("text"),
                "source_path": payload.get("source_path"),
            }
        )

    return retrieved_chunks