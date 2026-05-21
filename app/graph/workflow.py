from langgraph.graph import END, StateGraph
from langsmith import traceable

from app.graph.nodes import (
    answer_generation_node,
    escalation_node,
    evidence_check_node,
    query_rewrite_node,
    rerank_node,
    retrieval_node,
)
from app.graph.state import RAGState


def route_after_evidence_check(state: RAGState) -> str:
    if state.get("escalation_required"):
        return "escalation"

    return "answer_generation"


def build_rag_workflow():
    workflow = StateGraph(RAGState)

    workflow.add_node("query_rewrite", query_rewrite_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("rerank", rerank_node)
    workflow.add_node("evidence_check", evidence_check_node)
    workflow.add_node("answer_generation", answer_generation_node)
    workflow.add_node("escalation", escalation_node)

    workflow.set_entry_point("query_rewrite")

    workflow.add_edge("query_rewrite", "retrieval")
    workflow.add_edge("retrieval", "rerank")
    workflow.add_edge("rerank", "evidence_check")

    workflow.add_conditional_edges(
        "evidence_check",
        route_after_evidence_check,
        {
            "answer_generation": "answer_generation",
            "escalation": "escalation",
        },
    )

    workflow.add_edge("answer_generation", END)
    workflow.add_edge("escalation", END)

    return workflow.compile()


rag_workflow = build_rag_workflow()


@traceable(name="Run LangGraph RAG Workflow", run_type="chain")
def run_rag_workflow(
    question: str,
    top_k: int = 5,
    use_query_rewrite: bool = True,
    use_reranking: bool = True,
    department: str | None = None,
    document_type: str | None = None,
) -> RAGState:
    initial_state: RAGState = {
        "question": question,
        "top_k": top_k,
        "use_query_rewrite": use_query_rewrite,
        "use_reranking": use_reranking,
        "department": department,
        "document_type": document_type,
    }

    final_state = rag_workflow.invoke(initial_state)

    return final_state