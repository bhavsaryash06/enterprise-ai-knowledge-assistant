from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.repositories.document_repository import (
    create_document_record,
    get_document_by_source_path,
)


RAW_DOCUMENTS_DIR = Path("data/raw_documents")


def format_document_name(file_path: Path) -> str:
    name_without_extension = file_path.stem
    clean_name = name_without_extension.replace("_", " ").replace("-", " ")
    return clean_name.title()


def guess_department(file_name: str) -> str | None:
    lower_name = file_name.lower()

    if "finance" in lower_name or "expense" in lower_name or "reimbursement" in lower_name:
        return "Finance"

    if "hr" in lower_name or "leave" in lower_name or "onboarding" in lower_name:
        return "Human Resources"

    if "it" in lower_name or "security" in lower_name or "access" in lower_name or "device" in lower_name:
        return "Information Technology"

    if "privacy" in lower_name or "compliance" in lower_name:
        return "Compliance"

    if "incident" in lower_name:
        return "Operations"

    if "remote" in lower_name:
        return "Operations"

    return None


def register_documents_from_folder(db: Session) -> dict:
    RAW_DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    supported_files = list(RAW_DOCUMENTS_DIR.glob("*.txt")) + list(RAW_DOCUMENTS_DIR.glob("*.pdf"))

    registered_documents = []
    skipped_documents = []

    for file_path in supported_files:
        source_path = str(file_path).replace("\\", "/")

        existing_document = get_document_by_source_path(
            db=db,
            source_path=source_path,
        )

        if existing_document:
            skipped_documents.append(
                {
                    "file_name": file_path.name,
                    "reason": "already_registered",
                    "document_id": existing_document.document_id,
                }
            )
            continue

        document_id = f"{file_path.stem}_{uuid4().hex[:8]}"
        document_name = format_document_name(file_path)
        department = guess_department(file_path.name)

        document = create_document_record(
            db=db,
            document_id=document_id,
            file_name=file_path.name,
            document_name=document_name,
            department=department,
            document_type="Policy",
            version="v1",
            source_path=source_path,
        )

        registered_documents.append(
            {
                "document_id": document.document_id,
                "file_name": document.file_name,
                "document_name": document.document_name,
                "department": document.department,
                "status": document.status,
            }
        )

    return {
        "total_files_found": len(supported_files),
        "registered_count": len(registered_documents),
        "skipped_count": len(skipped_documents),
        "registered_documents": registered_documents,
        "skipped_documents": skipped_documents,
    }