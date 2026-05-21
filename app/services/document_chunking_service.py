from sqlalchemy.orm import Session

from app.repositories.chunk_repository import (
    create_chunk_record,
    delete_chunks_by_document_id,
    get_chunks_by_document_id,
)
from app.repositories.document_repository import update_document_status
from app.services.chunking_service import split_text_into_chunks
from app.services.document_processing_service import process_document_text


def chunk_document(
    db: Session,
    document_id: str,
    source_path: str,
) -> dict:
    update_document_status(
        db=db,
        document_id=document_id,
        status="chunking",
    )

    processed_result = process_document_text(source_path)
    cleaned_text = processed_result["text"]

    delete_chunks_by_document_id(
        db=db,
        document_id=document_id,
    )

    chunks = split_text_into_chunks(cleaned_text)

    saved_chunks = []

    for chunk in chunks:
        chunk_id = f"{document_id}_chunk_{chunk['chunk_number']:03d}"

        saved_chunk = create_chunk_record(
            db=db,
            chunk_id=chunk_id,
            document_id=document_id,
            chunk_number=chunk["chunk_number"],
            start_index=chunk["start_index"],
            end_index=chunk["end_index"],
            text=chunk["text"],
            text_length=chunk["text_length"],
        )

        saved_chunks.append(saved_chunk)

    update_document_status(
        db=db,
        document_id=document_id,
        status="chunked",
    )

    return {
        "document_id": document_id,
        "status": "chunked",
        "total_chunks": len(saved_chunks),
        "raw_text_length": processed_result["raw_text_length"],
        "cleaned_text_length": processed_result["cleaned_text_length"],
    }


def get_document_chunks_summary(
    db: Session,
    document_id: str,
) -> dict:
    chunks = get_chunks_by_document_id(
        db=db,
        document_id=document_id,
    )

    return {
        "document_id": document_id,
        "total_chunks": len(chunks),
        "chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "chunk_number": chunk.chunk_number,
                "text_length": chunk.text_length,
                "text_preview": chunk.text[:200],
            }
            for chunk in chunks
        ],
    }