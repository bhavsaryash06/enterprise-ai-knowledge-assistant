from pathlib import Path

from sqlalchemy.orm import Session

from app.repositories.document_repository import get_all_documents
from app.services.document_chunking_service import chunk_document
from app.services.qdrant_indexing_service import index_document_chunks


def bulk_chunk_documents(db: Session) -> dict:
    documents = get_all_documents(db)

    chunked_documents = []
    skipped_documents = []
    failed_documents = []

    for document in documents:
        source_path = Path(document.source_path)

        if not source_path.exists():
            skipped_documents.append(
                {
                    "document_id": document.document_id,
                    "file_name": document.file_name,
                    "reason": "source_file_not_found",
                }
            )
            continue

        try:
            result = chunk_document(
                db=db,
                document_id=document.document_id,
                source_path=document.source_path,
            )

            chunked_documents.append(result)

        except Exception as error:
            failed_documents.append(
                {
                    "document_id": document.document_id,
                    "file_name": document.file_name,
                    "error": str(error),
                }
            )

    return {
        "total_documents": len(documents),
        "chunked_count": len(chunked_documents),
        "skipped_count": len(skipped_documents),
        "failed_count": len(failed_documents),
        "chunked_documents": chunked_documents,
        "skipped_documents": skipped_documents,
        "failed_documents": failed_documents,
    }


def bulk_index_documents(db: Session) -> dict:
    documents = get_all_documents(db)

    indexed_documents = []
    skipped_documents = []
    failed_documents = []

    for document in documents:
        source_path = Path(document.source_path)

        if not source_path.exists():
            skipped_documents.append(
                {
                    "document_id": document.document_id,
                    "file_name": document.file_name,
                    "status": document.status,
                    "reason": "source_file_not_found",
                }
            )
            continue

        if document.status not in ["chunked", "indexed"]:
            skipped_documents.append(
                {
                    "document_id": document.document_id,
                    "file_name": document.file_name,
                    "status": document.status,
                    "reason": "document_not_chunked_or_indexed",
                }
            )
            continue

        try:
            result = index_document_chunks(
                db=db,
                document_id=document.document_id,
            )

            indexed_documents.append(result)

        except Exception as error:
            failed_documents.append(
                {
                    "document_id": document.document_id,
                    "file_name": document.file_name,
                    "error": str(error),
                }
            )

    return {
        "total_documents": len(documents),
        "indexed_count": len(indexed_documents),
        "skipped_count": len(skipped_documents),
        "failed_count": len(failed_documents),
        "indexed_documents": indexed_documents,
        "skipped_documents": skipped_documents,
        "failed_documents": failed_documents,
    }