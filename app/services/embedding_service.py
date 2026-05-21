from openai import OpenAI

from app.core.config import settings


def get_openai_client() -> OpenAI:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set. Please add it to your .env file.")

    return OpenAI(api_key=settings.openai_api_key)


def create_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty when creating an embedding.")

    client = get_openai_client()

    response = client.embeddings.create(
        model=settings.embedding_model,
        input=text,
    )

    return response.data[0].embedding


def create_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    cleaned_texts = [text.strip() for text in texts if text and text.strip()]

    if not cleaned_texts:
        return []

    client = get_openai_client()

    response = client.embeddings.create(
        model=settings.embedding_model,
        input=cleaned_texts,
    )

    return [item.embedding for item in response.data]