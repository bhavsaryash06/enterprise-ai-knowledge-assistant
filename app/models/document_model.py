from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(100), unique=True, index=True, nullable=False)
    file_name = Column(String(255), nullable=False)
    document_name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=True)
    document_type = Column(String(100), nullable=True)
    version = Column(String(50), nullable=True)
    status = Column(String(50), default="uploaded", nullable=False)
    source_path = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)