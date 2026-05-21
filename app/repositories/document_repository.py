from sqlalchemy.orm import Session

from app.models.document_model import Document


def create_document_record(
    db: Session,
    document_id: str,
    file_name: str,
    document_name: str,
    source_path: str,
    department: str | None = None,
    document_type: str | None = None,
    version: str | None = None,
) -> Document:
    document = Document(
        document_id=document_id,
        file_name=file_name,
        document_name=document_name,
        department=department,
        document_type=document_type,
        version=version,
        source_path=source_path,
        status="uploaded",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_all_documents(db: Session) -> list[Document]:
    return db.query(Document).order_by(Document.created_at.desc()).all()


def get_document_by_id(db: Session, document_id: str) -> Document | None:
    return db.query(Document).filter(Document.document_id == document_id).first()


def get_document_by_source_path(db: Session, source_path: str) -> Document | None:
    return db.query(Document).filter(Document.source_path == source_path).first()


def update_document_status(
    db: Session,
    document_id: str,
    status: str,
) -> Document | None:
    document = get_document_by_id(db=db, document_id=document_id)

    if document is None:
        return None

    document.status = status
    db.commit()
    db.refresh(document)

    return document