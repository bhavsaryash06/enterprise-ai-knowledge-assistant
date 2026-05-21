from fastapi import FastAPI

from app.api.ask_routes import router as ask_router
from app.api.document_routes import router as document_router
from app.api.health_routes import router as health_router
from app.core.config import settings
from app.core.tracing import configure_langsmith_tracing


configure_langsmith_tracing()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Production-style enterprise AI knowledge assistant using RAG, Qdrant, LangGraph, FastAPI, and Azure deployment.",
)


app.include_router(health_router)
app.include_router(document_router)
app.include_router(ask_router)


@app.get("/")
def root():
    return {
        "message": "Enterprise AI Knowledge Assistant API is running",
        "docs_url": "/docs",
        "health_url": "/health/",
        "documents_url": "/documents/",
        "retrieve_url": "/ask/retrieve",
        "graph_ask_url": "/ask/graph",
    }