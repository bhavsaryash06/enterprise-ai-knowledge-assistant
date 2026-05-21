from langsmith import traceable

from app.graph.state import RAGState
from app.services.answer_generator import generate_answer_from_chunks
from app.services.citation_service import build_citations
from app.services.evidence_checker import assess_evidence_strength
from app.services.query_rewriter import rewrite_query_for_retrieval
from app.services.reranker_service import rerank_chunks
from app.services.retriever_service import retrieve_relevant_chunks


@traceable(name="Graph Node - Query Rewrite", run_type="chain")
def query_rewrite_node(state: RAGState) -> RAGState:
    question = state["question"]
    use_query_rewrite = state.get("use_query_rewrite", True)

    if use_query_rewrite:
        rewritten_query = rewrite_query_for_retrieval(question)
        retrieval_query = rewritten_query
    else:
        rewritten_query = None
        retrieval_query = question

    return {
        "rewritten_query": rewritten_query,
        "retrieval_query": retrieval_query,
    }


@traceable(name="Graph Node - Retrieval", run_type="retriever")
def retrieval_node(state: RAGState) -> RAGState:
    retrieval_query = state.get("retrieval_query") or state["question"]
    top_k = state.get("top_k", 5)
    use_reranking = state.get("use_reranking", True)

    retrieval_top_k = top_k * 2 if use_reranking else top_k

    retrieved_chunks = retrieve_relevant_chunks(
        query=retrieval_query,
        top_k=retrieval_top_k,
        department=state.get("department"),
        document_type=state.get("document_type"),
    )

    return {
        "retrieved_chunks": retrieved_chunks,
    }


@traceable(name="Graph Node - Rerank", run_type="chain")
def rerank_node(state: RAGState) -> RAGState:
    question = state["question"]
    retrieved_chunks = state.get("retrieved_chunks", [])
    top_k = state.get("top_k", 5)
    use_reranking = state.get("use_reranking", True)

    if not use_reranking:
        return {
            "retrieved_chunks": retrieved_chunks[:top_k],
        }

    reranked_chunks = rerank_chunks(
        question=question,
        retrieved_chunks=retrieved_chunks,
        top_k=top_k,
    )

    return {
        "retrieved_chunks": reranked_chunks,
    }


@traceable(name="Graph Node - Evidence Check", run_type="chain")
def evidence_check_node(state: RAGState) -> RAGState:
    retrieved_chunks = state.get("retrieved_chunks", [])

    evidence_result = assess_evidence_strength(retrieved_chunks)
    citations = build_citations(retrieved_chunks)

    return {
        "confidence": evidence_result["confidence"],
        "escalation_required": evidence_result["escalation_required"],
        "evidence_reason": evidence_result["reason"],
        "top_score": evidence_result["top_score"],
        "sources": citations,
    }


@traceable(name="Graph Node - Escalation", run_type="chain")
def escalation_node(state: RAGState) -> RAGState:
    return {
        "answer": (
            "I could not find strong enough evidence in the company documents "
            "to answer this question confidently. Please escalate this to the appropriate department."
        ),
        "confidence": state.get("confidence", "low"),
        "escalation_required": True,
        "evidence_reason": state.get("evidence_reason"),
        "top_score": state.get("top_score"),
        "sources": state.get("sources", []),
    }


@traceable(name="Graph Node - Answer Generation", run_type="llm")
def answer_generation_node(state: RAGState) -> RAGState:
    question = state["question"]
    retrieved_chunks = state.get("retrieved_chunks", [])

    answer_result = generate_answer_from_chunks(
        question=question,
        retrieved_chunks=retrieved_chunks,
    )

    return {
        "answer": answer_result["answer"],
        "confidence": answer_result["confidence"],
        "escalation_required": answer_result["escalation_required"],
        "evidence_reason": answer_result.get("evidence_reason"),
        "top_score": answer_result.get("top_score"),
        "sources": answer_result["sources"],
    }