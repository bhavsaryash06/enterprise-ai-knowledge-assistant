from langsmith import traceable
from openai import OpenAI

from app.core.config import settings


def get_openai_client() -> OpenAI:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set. Please add it to your .env file.")

    return OpenAI(api_key=settings.openai_api_key)


@traceable(name="Rewrite Query For Retrieval", run_type="llm")
def rewrite_query_for_retrieval(question: str) -> str:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    client = get_openai_client()

    system_prompt = """
You rewrite employee questions into better search queries for an enterprise policy RAG system.

Rules:
- Keep the meaning of the original question.
- Add likely enterprise policy terms.
- Do not answer the question.
- Do not invent facts.
- Return only the rewritten search query.
- Keep it short, clear, and keyword-rich.
"""

    user_prompt = f"""
Original employee question:
{question}

Rewrite this as a search query for retrieving company policy documents.
"""

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.1,
    )

    rewritten_query = response.choices[0].message.content.strip()

    if not rewritten_query:
        return question.strip()

    return rewritten_query