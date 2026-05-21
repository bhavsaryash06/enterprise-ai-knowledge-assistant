from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import settings


VECTOR_SIZE = 1536


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
    )


def check_qdrant_connection() -> dict:
    try:
        client = get_qdrant_client()
        collections = client.get_collections()

        return {
            "status": "ok",
            "collections": [collection.name for collection in collections.collections],
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
        }


def create_collection_if_not_exists() -> dict:
    client = get_qdrant_client()

    existing_collections = client.get_collections().collections
    existing_collection_names = [
        collection.name for collection in existing_collections
    ]

    if settings.qdrant_collection_name in existing_collection_names:
        return {
            "status": "exists",
            "collection_name": settings.qdrant_collection_name,
        }

    client.create_collection(
        collection_name=settings.qdrant_collection_name,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

    return {
        "status": "created",
        "collection_name": settings.qdrant_collection_name,
    }