from fastapi import APIRouter, HTTPException

from app.core.logger import logger
from app.core.metrics import log_latency
from app.graph.workflow import run_rag_workflow
from app.schemas.ask_schema import (
    AskRequest,
    AskResponse,
    RetrievalRequest,
    RetrievalResponse,
)
from app.services.answer_generator import generate_answer_from_chunks
from app.services.retrieval_pipeline_service import run_retrieval_pipeline


router = APIRouter(prefix="/ask", tags=["Ask"])


@router.post("/retrieve", response_model=RetrievalResponse)
def retrieve_chunks(request: RetrievalRequest):
    try:
        logger.info(
            "Retrieval request received | question=%s | top_k=%s | rewrite=%s | reranking=%s | department=%s | document_type=%s",
            request.question,
            request.top_k,
            request.use_query_rewrite,
            request.use_reranking,
            request.department,
            request.document_type,
        )

        with log_latency("api_retrieve_chunks"):
            retrieval_result = run_retrieval_pipeline(
                question=request.question,
                top_k=request.top_k,
                use_query_rewrite=request.use_query_rewrite,
                use_reranking=request.use_reranking,
                department=request.department,
                document_type=request.document_type,
            )

        logger.info(
            "Retrieval request completed | question=%s | total_results=%s",
            request.question,
            retrieval_result["total_results"],
        )

        return {
            "question": retrieval_result["question"],
            "rewritten_query": retrieval_result["rewritten_query"],
            "total_results": retrieval_result["total_results"],
            "retrieved_chunks": retrieval_result["retrieved_chunks"],
        }

    except Exception as error:
        logger.exception(
            "Retrieval request failed | question=%s | error=%s",
            request.question,
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.post("/", response_model=AskResponse)
def ask_question(request: AskRequest):
    try:
        logger.info(
            "Standard ask request received | question=%s | top_k=%s | rewrite=%s | reranking=%s | department=%s | document_type=%s",
            request.question,
            request.top_k,
            request.use_query_rewrite,
            request.use_reranking,
            request.department,
            request.document_type,
        )

        with log_latency("api_standard_ask_total"):
            with log_latency("api_standard_ask_retrieval"):
                retrieval_result = run_retrieval_pipeline(
                    question=request.question,
                    top_k=request.top_k,
                    use_query_rewrite=request.use_query_rewrite,
                    use_reranking=request.use_reranking,
                    department=request.department,
                    document_type=request.document_type,
                )

            with log_latency("api_standard_ask_answer_generation"):
                answer_result = generate_answer_from_chunks(
                    question=request.question,
                    retrieved_chunks=retrieval_result["retrieved_chunks"],
                )

        logger.info(
            "Standard ask request completed | question=%s | confidence=%s | escalation_required=%s | retrieved_chunks=%s",
            request.question,
            answer_result["confidence"],
            answer_result["escalation_required"],
            len(retrieval_result["retrieved_chunks"]),
        )

        return {
            "question": request.question,
            "rewritten_query": retrieval_result["rewritten_query"],
            "answer": answer_result["answer"],
            "confidence": answer_result["confidence"],
            "escalation_required": answer_result["escalation_required"],
            "evidence_reason": answer_result.get("evidence_reason"),
            "top_score": answer_result.get("top_score"),
            "sources": answer_result["sources"],
            "retrieved_chunks": retrieval_result["retrieved_chunks"],
        }

    except Exception as error:
        logger.exception(
            "Standard ask request failed | question=%s | error=%s",
            request.question,
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.post("/graph", response_model=AskResponse)
def ask_question_with_graph(request: AskRequest):
    try:
        logger.info(
            "LangGraph ask request received | question=%s | top_k=%s | rewrite=%s | reranking=%s | department=%s | document_type=%s",
            request.question,
            request.top_k,
            request.use_query_rewrite,
            request.use_reranking,
            request.department,
            request.document_type,
        )

        with log_latency("api_langgraph_ask_total"):
            final_state = run_rag_workflow(
                question=request.question,
                top_k=request.top_k,
                use_query_rewrite=request.use_query_rewrite,
                use_reranking=request.use_reranking,
                department=request.department,
                document_type=request.document_type,
            )

        logger.info(
            "LangGraph ask request completed | question=%s | confidence=%s | escalation_required=%s | retrieved_chunks=%s",
            request.question,
            final_state["confidence"],
            final_state["escalation_required"],
            len(final_state["retrieved_chunks"]),
        )

        return {
            "question": final_state["question"],
            "rewritten_query": final_state.get("rewritten_query"),
            "answer": final_state["answer"],
            "confidence": final_state["confidence"],
            "escalation_required": final_state["escalation_required"],
            "evidence_reason": final_state.get("evidence_reason"),
            "top_score": final_state.get("top_score"),
            "sources": final_state["sources"],
            "retrieved_chunks": final_state["retrieved_chunks"],
        }

    except Exception as error:
        logger.exception(
            "LangGraph ask request failed | question=%s | error=%s",
            request.question,
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )