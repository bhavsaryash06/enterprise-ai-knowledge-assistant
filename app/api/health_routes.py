from fastapi import APIRouter

from app.core.config import settings
from app.services.qdrant_service import check_qdrant_connection


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
def health_check():
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.app_env,
    }


@router.get("/qdrant")
def qdrant_health_check():
    return check_qdrant_connection()