from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.database import get_db
from app.repositories.document_repository import (
    create_document_record,
    get_all_documents,
    get_document_by_id,
    update_document_status,
)
from app.schemas.document_schema import DocumentResponse
from app.services.document_chunking_service import (
    chunk_document,
    get_document_chunks_summary,
)
from app.services.document_processing_service import process_document_text
from app.services.qdrant_indexing_service import index_document_chunks


router = APIRouter(prefix="/documents", tags=["Documents"])

RAW_DOCUMENTS_DIR = Path("data/raw_documents")
RAW_DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    try:
        logger.info("List documents request received")

        documents = get_all_documents(db)

        logger.info(
            "List documents request completed | total_documents=%s",
            len(documents),
        )

        return documents

    except Exception as error:
        logger.exception(
            "List documents request failed | error=%s",
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_name: str = Form(...),
    department: str | None = Form(None),
    document_type: str | None = Form(None),
    version: str | None = Form(None),
    db: Session = Depends(get_db),
):
    try:
        logger.info(
            "Document upload request received | file_name=%s | document_name=%s | department=%s | document_type=%s | version=%s",
            file.filename,
            document_name,
            department,
            document_type,
            version,
        )

        file_extension = Path(file.filename).suffix
        document_id = f"{Path(file.filename).stem}_{uuid4().hex[:8]}"
        saved_file_name = f"{document_id}{file_extension}"
        saved_file_path = RAW_DOCUMENTS_DIR / saved_file_name

        file_bytes = await file.read()

        with open(saved_file_path, "wb") as output_file:
            output_file.write(file_bytes)

        document = create_document_record(
            db=db,
            document_id=document_id,
            file_name=file.filename,
            document_name=document_name,
            department=department,
            document_type=document_type,
            version=version,
            source_path=str(saved_file_path),
        )

        logger.info(
            "Document upload completed | document_id=%s | saved_path=%s | status=%s",
            document.document_id,
            document.source_path,
            document.status,
        )

        return document

    except Exception as error:
        logger.exception(
            "Document upload failed | file_name=%s | error=%s",
            file.filename if file else None,
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.post("/{document_id}/process")
def process_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    document = get_document_by_id(db=db, document_id=document_id)

    if document is None:
        logger.warning(
            "Document process request failed | document_id=%s | reason=document_not_found",
            document_id,
        )

        raise HTTPException(
            status_code=404,
            detail=f"Document with id '{document_id}' was not found.",
        )

    try:
        logger.info(
            "Document processing started | document_id=%s | source_path=%s",
            document.document_id,
            document.source_path,
        )

        update_document_status(
            db=db,
            document_id=document_id,
            status="processing",
        )

        result = process_document_text(document.source_path)

        update_document_status(
            db=db,
            document_id=document_id,
            status="processed",
        )

        logger.info(
            "Document processing completed | document_id=%s | raw_text_length=%s | cleaned_text_length=%s",
            document.document_id,
            result["raw_text_length"],
            result["cleaned_text_length"],
        )

        return {
            "document_id": document.document_id,
            "document_name": document.document_name,
            "status": "processed",
            "raw_text_length": result["raw_text_length"],
            "cleaned_text_length": result["cleaned_text_length"],
            "text_preview": result["text"][:500],
        }

    except Exception as error:
        update_document_status(
            db=db,
            document_id=document_id,
            status="failed",
        )

        logger.exception(
            "Document processing failed | document_id=%s | error=%s",
            document_id,
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.post("/{document_id}/chunk")
def chunk_uploaded_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    document = get_document_by_id(db=db, document_id=document_id)

    if document is None:
        logger.warning(
            "Document chunk request failed | document_id=%s | reason=document_not_found",
            document_id,
        )

        raise HTTPException(
            status_code=404,
            detail=f"Document with id '{document_id}' was not found.",
        )

    try:
        logger.info(
            "Document chunking started | document_id=%s | source_path=%s",
            document.document_id,
            document.source_path,
        )

        result = chunk_document(
            db=db,
            document_id=document.document_id,
            source_path=document.source_path,
        )

        logger.info(
            "Document chunking completed | document_id=%s | total_chunks=%s",
            document.document_id,
            result["total_chunks"],
        )

        return result

    except Exception as error:
        update_document_status(
            db=db,
            document_id=document_id,
            status="failed",
        )

        logger.exception(
            "Document chunking failed | document_id=%s | error=%s",
            document_id,
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.get("/{document_id}/chunks")
def list_document_chunks(
    document_id: str,
    db: Session = Depends(get_db),
):
    document = get_document_by_id(db=db, document_id=document_id)

    if document is None:
        logger.warning(
            "List document chunks request failed | document_id=%s | reason=document_not_found",
            document_id,
        )

        raise HTTPException(
            status_code=404,
            detail=f"Document with id '{document_id}' was not found.",
        )

    try:
        logger.info(
            "List document chunks request received | document_id=%s",
            document_id,
        )

        result = get_document_chunks_summary(
            db=db,
            document_id=document_id,
        )

        logger.info(
            "List document chunks request completed | document_id=%s | total_chunks=%s",
            document_id,
            result["total_chunks"],
        )

        return result

    except Exception as error:
        logger.exception(
            "List document chunks request failed | document_id=%s | error=%s",
            document_id,
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.post("/{document_id}/index")
def index_uploaded_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    document = get_document_by_id(db=db, document_id=document_id)

    if document is None:
        logger.warning(
            "Document index request failed | document_id=%s | reason=document_not_found",
            document_id,
        )

        raise HTTPException(
            status_code=404,
            detail=f"Document with id '{document_id}' was not found.",
        )

    try:
        logger.info(
            "Document indexing started | document_id=%s | document_name=%s",
            document.document_id,
            document.document_name,
        )

        result = index_document_chunks(
            db=db,
            document_id=document.document_id,
        )

        logger.info(
            "Document indexing completed | document_id=%s | indexed_chunks=%s | collection=%s",
            document.document_id,
            result["indexed_chunks"],
            result["collection_name"],
        )

        return result

    except Exception as error:
        update_document_status(
            db=db,
            document_id=document_id,
            status="failed",
        )

        logger.exception(
            "Document indexing failed | document_id=%s | error=%s",
            document_id,
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )