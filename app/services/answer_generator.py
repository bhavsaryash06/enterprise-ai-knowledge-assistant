from openai import OpenAI

from app.core.config import settings
from app.services.citation_service import build_citations
from app.services.evidence_checker import assess_evidence_strength


def get_openai_client() -> OpenAI:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set. Please add it to your .env file.")

    return OpenAI(api_key=settings.openai_api_key)


def format_context_from_chunks(retrieved_chunks: list[dict]) -> str:
    context_parts = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        context_parts.append(
            f"""
Source {index}
Document: {chunk.get("document_name")}
Department: {chunk.get("department")}
Version: {chunk.get("version")}
Chunk ID: {chunk.get("chunk_id")}
Vector Score: {chunk.get("score")}
Rerank Score: {chunk.get("rerank_score")}
Text:
{chunk.get("text")}
"""
        )

    return "\n".join(context_parts)


def generate_answer_from_chunks(
    question: str,
    retrieved_chunks: list[dict],
) -> dict:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    evidence_result = assess_evidence_strength(retrieved_chunks)
    citations = build_citations(retrieved_chunks)

    if evidence_result["escalation_required"]:
        return {
            "answer": (
                "I could not find strong enough evidence in the company documents "
                "to answer this question confidently. Please escalate this to the appropriate department."
            ),
            "confidence": evidence_result["confidence"],
            "sources": citations,
            "escalation_required": True,
            "evidence_reason": evidence_result["reason"],
            "top_score": evidence_result["top_score"],
        }

    client = get_openai_client()
    context = format_context_from_chunks(retrieved_chunks)

    system_prompt = """
You are an enterprise AI knowledge assistant for internal company policy questions.

Your rules:
- Answer only using the provided company document context.
- Do not invent company policies.
- Do not use outside knowledge.
- If the provided context does not support a detail, do not include that detail.
- Use source numbers clearly, such as Source 1, Source 2, or Source 3.
- Be practical and complete, not overly short.
- Include relevant limits, deadlines, approvals, responsible teams, exceptions, and required actions when they appear in the sources.
- If evidence is incomplete or only partially related, clearly say what can and cannot be confirmed.
"""

    user_prompt = f"""
User question:
{question}

Evidence confidence:
{evidence_result["confidence"]}

Evidence reason:
{evidence_result["reason"]}

Company document context:
{context}

Write the answer using this structure:

1. Direct answer
- Start with yes/no or the direct policy answer when possible.

2. Required actions
- Mention what the employee must do.
- Include reporting steps, submission steps, approval steps, or required systems if the sources mention them.

3. Limits, deadlines, approvals, or conditions
- Include reimbursement limits, deadlines, required approvals, documentation, training deadlines, review timelines, or exceptions if the sources mention them.

4. Responsible team or escalation path
- Mention the responsible team such as Finance, HR, IT Security, Compliance, manager, department head, or Facilities if the sources mention them.

5. Sources used
- List the source numbers used.
- Do not cite a source unless it supports the answer.

6. Human review
- Say whether human review is needed.
- If the policy is clear, say human review is not needed.
- If the evidence is incomplete, conflicting, or only partially related, recommend human review.

Important:
- Do not skip relevant conditions just because the question is short.
- Do not give a one-sentence answer unless the policy evidence is extremely simple.
- Keep the answer concise but complete.
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

    answer_text = response.choices[0].message.content

    return {
        "answer": answer_text,
        "confidence": evidence_result["confidence"],
        "sources": citations,
        "escalation_required": evidence_result["escalation_required"],
        "evidence_reason": evidence_result["reason"],
        "top_score": evidence_result["top_score"],
    }