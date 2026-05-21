from langsmith import traceable

from app.core.metrics import log_latency
from app.services.query_rewriter import rewrite_query_for_retrieval
from app.services.reranker_service import rerank_chunks
from app.services.retriever_service import retrieve_relevant_chunks


@traceable(name="Run Retrieval Pipeline", run_type="chain")
def run_retrieval_pipeline(
    question: str,
    top_k: int = 5,
    use_query_rewrite: bool = True,
    use_reranking: bool = True,
    department: str | None = None,
    document_type: str | None = None,
) -> dict:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    with log_latency("retrieval_pipeline_total"):
        rewritten_query = None
        retrieval_query = question

        if use_query_rewrite:
            with log_latency("retrieval_pipeline_query_rewrite"):
                rewritten_query = rewrite_query_for_retrieval(question)
                retrieval_query = rewritten_query

        retrieval_top_k = top_k * 2 if use_reranking else top_k

        with log_latency("retrieval_pipeline_vector_search"):
            retrieved_chunks = retrieve_relevant_chunks(
                query=retrieval_query,
                top_k=retrieval_top_k,
                department=department,
                document_type=document_type,
            )

        if use_reranking:
            with log_latency("retrieval_pipeline_reranking"):
                retrieved_chunks = rerank_chunks(
                    question=question,
                    retrieved_chunks=retrieved_chunks,
                    top_k=top_k,
                )

        return {
            "question": question,
            "rewritten_query": rewritten_query,
            "retrieval_query": retrieval_query,
            "retrieved_chunks": retrieved_chunks,
            "total_results": len(retrieved_chunks),
            "used_query_rewrite": use_query_rewrite,
            "used_reranking": use_reranking,
            "department_filter": department,
            "document_type_filter": document_type,
        }