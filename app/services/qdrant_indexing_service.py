from uuid import NAMESPACE_DNS, uuid5

from qdrant_client.models import PointStruct
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import logger
from app.core.metrics import log_latency
from app.repositories.chunk_repository import get_chunks_by_document_id
from app.repositories.document_repository import (
    get_document_by_id,
    update_document_status,
)
from app.services.embedding_service import create_embeddings
from app.services.qdrant_service import (
    create_collection_if_not_exists,
    get_qdrant_client,
)


def create_qdrant_point_id(chunk_id: str) -> str:
    return str(uuid5(NAMESPACE_DNS, chunk_id))


def index_document_chunks(
    db: Session,
    document_id: str,
) -> dict:
    with log_latency("document_indexing_total"):
        document = get_document_by_id(db=db, document_id=document_id)

        if document is None:
            raise ValueError(f"Document with id '{document_id}' was not found.")

        chunks = get_chunks_by_document_id(
            db=db,
            document_id=document_id,
        )

        if not chunks:
            raise ValueError(
                f"No chunks found for document '{document_id}'. Please chunk the document first."
            )

        logger.info(
            "Document indexing service started | document_id=%s | chunks=%s",
            document_id,
            len(chunks),
        )

        update_document_status(
            db=db,
            document_id=document_id,
            status="indexing",
        )

        with log_latency("document_indexing_create_collection"):
            create_collection_if_not_exists()

        chunk_texts = [chunk.text for chunk in chunks]

        with log_latency("document_indexing_create_embeddings"):
            embeddings = create_embeddings(chunk_texts)

        if len(embeddings) != len(chunks):
            raise ValueError("Number of embeddings does not match number of chunks.")

        points = []

        with log_latency("document_indexing_build_qdrant_points"):
            for chunk, embedding in zip(chunks, embeddings):
                point = PointStruct(
                    id=create_qdrant_point_id(chunk.chunk_id),
                    vector=embedding,
                    payload={
                        "chunk_id": chunk.chunk_id,
                        "document_id": document.document_id,
                        "document_name": document.document_name,
                        "file_name": document.file_name,
                        "department": document.department,
                        "document_type": document.document_type,
                        "version": document.version,
                        "source_path": document.source_path,
                        "chunk_number": chunk.chunk_number,
                        "text": chunk.text,
                        "text_length": chunk.text_length,
                    },
                )

                points.append(point)

        client = get_qdrant_client()

        with log_latency("document_indexing_qdrant_upsert"):
            client.upsert(
                collection_name=settings.qdrant_collection_name,
                points=points,
            )

        update_document_status(
            db=db,
            document_id=document_id,
            status="indexed",
        )

        logger.info(
            "Document indexing service completed | document_id=%s | indexed_chunks=%s | collection=%s",
            document_id,
            len(points),
            settings.qdrant_collection_name,
        )

        return {
            "document_id": document_id,
            "status": "indexed",
            "indexed_chunks": len(points),
            "collection_name": settings.qdrant_collection_name,
        }