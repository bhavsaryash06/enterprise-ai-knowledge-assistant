from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.db.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String(150), unique=True, index=True, nullable=False)
    document_id = Column(String(100), ForeignKey("documents.document_id"), index=True, nullable=False)
    chunk_number = Column(Integer, nullable=False)
    start_index = Column(Integer, nullable=False)
    end_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    text_length = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)