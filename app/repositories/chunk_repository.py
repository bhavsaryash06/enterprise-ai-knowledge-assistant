from sqlalchemy.orm import Session

from app.models.document_model import Document
from app.models.chunk_model import DocumentChunk


def create_chunk_record(
    db: Session,
    chunk_id: str,
    document_id: str,
    chunk_number: int,
    start_index: int,
    end_index: int,
    text: str,
    text_length: int,
) -> DocumentChunk:
    chunk = DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        chunk_number=chunk_number,
        start_index=start_index,
        end_index=end_index,
        text=text,
        text_length=text_length,
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    return chunk


def get_chunks_by_document_id(
    db: Session,
    document_id: str,
) -> list[DocumentChunk]:
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_number.asc())
        .all()
    )


def delete_chunks_by_document_id(
    db: Session,
    document_id: str,
) -> int:
    deleted_count = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .delete()
    )

    db.commit()

    return deleted_count