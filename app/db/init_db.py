from app.db.database import Base, engine
from app.models.document_model import Document
from app.models.chunk_model import DocumentChunk


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")