from datetime import datetime

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    document_id: str
    file_name: str
    document_name: str
    source_path: str
    department: str | None = None
    document_type: str | None = None
    version: str | None = None


class DocumentResponse(BaseModel):
    id: int
    document_id: str
    file_name: str
    document_name: str
    department: str | None = None
    document_type: str | None = None
    version: str | None = None
    status: str
    source_path: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class DocumentStatusUpdate(BaseModel):
    status: str