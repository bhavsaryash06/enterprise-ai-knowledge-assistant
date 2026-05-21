import json
from pathlib import Path
from typing import Any

from app.services.retrieval_pipeline_service import run_retrieval_pipeline


EVAL_DATASET_PATH = Path("app/evaluation/eval_dataset.json")
REPORT_OUTPUT_PATH = Path("app/evaluation/retrieval_eval_report.json")


def load_eval_dataset() -> list[dict[str, Any]]:
    with open(EVAL_DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_text(value: str) -> str:
    return value.strip().lower()


def get_retrieved_document_names(retrieved_chunks: list[dict[str, Any]]) -> list[str]:
    document_names = []

    for chunk in retrieved_chunks:
        document_name = chunk.get("document_name")

        if document_name and document_name not in document_names:
            document_names.append(document_name)

    return document_names


def calculate_source_recall(
    expected_sources: list[str],
    retrieved_sources: list[str],
) -> dict[str, Any]:
    normalized_expected = [normalize_text(source) for source in expected_sources]
    normalized_retrieved = [normalize_text(source) for source in retrieved_sources]

    matched_sources = []

    for expected_source in normalized_expected:
        if expected_source in normalized_retrieved:
            matched_sources.append(expected_source)

    if not expected_sources:
        return {
            "matched_sources": [],
            "source_recall": None,
        }

    source_recall = len(matched_sources) / len(expected_sources)

    return {
        "matched_sources": matched_sources,
        "source_recall": source_recall,
    }


def get_result_status(expected_behavior: str, source_recall: float | None) -> str:
    if expected_behavior == "escalate":
        return "unsupported_not_scored_for_retrieval"

    if source_recall == 1.0:
        return "pass"

    if source_recall and source_recall > 0:
        return "partial"

    return "fail"


def run_retrieval_evaluation() -> dict[str, Any]:
    dataset = load_eval_dataset()

    results = []
    supported_recalls = []
    supported_top_source_matches = 0
    supported_count = 0
    unsupported_count = 0

    for item in dataset:
        question = item["question"]
        expected_behavior = item["expected_behavior"]
        expected_sources = item["expected_source_documents"]

        try:
            retrieval_result = run_retrieval_pipeline(
                question=question,
                top_k=5,
                use_query_rewrite=True,
                use_reranking=True,
                document_type="Policy",
            )

            retrieved_chunks = retrieval_result["retrieved_chunks"]
            retrieved_sources = get_retrieved_document_names(retrieved_chunks)

            source_match = calculate_source_recall(
                expected_sources=expected_sources,
                retrieved_sources=retrieved_sources,
            )

            source_recall = source_match["source_recall"]
            matched_sources = source_match["matched_sources"]
            top_retrieved_source = retrieved_sources[0] if retrieved_sources else None

            if expected_behavior == "answer":
                supported_count += 1

                if source_recall is not None:
                    supported_recalls.append(source_recall)

                normalized_expected_sources = [
                    normalize_text(source) for source in expected_sources
                ]

                if (
                    top_retrieved_source
                    and normalize_text(top_retrieved_source) in normalized_expected_sources
                ):
                    supported_top_source_matches += 1

            else:
                unsupported_count += 1

            result = {
                "id": item["id"],
                "question": question,
                "category": item["category"],
                "expected_behavior": expected_behavior,
                "expected_sources": expected_sources,
                "retrieved_sources": retrieved_sources,
                "source_recall": source_recall,
                "matched_sources": matched_sources,
                "top_retrieved_source": top_retrieved_source,
                "status": get_result_status(expected_behavior, source_recall),
            }

            results.append(result)

        except Exception as error:
            results.append(
                {
                    "id": item["id"],
                    "question": question,
                    "category": item["category"],
                    "expected_behavior": expected_behavior,
                    "expected_sources": expected_sources,
                    "retrieved_sources": [],
                    "source_recall": None,
                    "matched_sources": [],
                    "top_retrieved_source": None,
                    "status": "error",
                    "error": str(error),
                }
            )

    supported_average_source_recall = (
        sum(supported_recalls) / len(supported_recalls)
        if supported_recalls
        else 0.0
    )

    supported_top_source_accuracy = (
        supported_top_source_matches / supported_count
        if supported_count
        else 0.0
    )

    pass_count = len([result for result in results if result["status"] == "pass"])
    partial_count = len([result for result in results if result["status"] == "partial"])
    fail_count = len([result for result in results if result["status"] == "fail"])
    error_count = len([result for result in results if result["status"] == "error"])

    evaluation_summary = {
        "total_questions": len(results),
        "supported_questions": supported_count,
        "unsupported_questions": unsupported_count,
        "supported_average_source_recall": supported_average_source_recall,
        "supported_top_source_accuracy": supported_top_source_accuracy,
        "pass_count": pass_count,
        "partial_count": partial_count,
        "fail_count": fail_count,
        "error_count": error_count,
        "note": (
            "Unsupported questions are not scored using source recall because vector search "
            "will usually return some nearest chunks. Unsupported behavior should be evaluated "
            "with answer/escalation evaluation."
        ),
        "results": results,
    }

    return evaluation_summary


def save_report(report: dict[str, Any]) -> None:
    REPORT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


if __name__ == "__main__":
    evaluation_result = run_retrieval_evaluation()
    save_report(evaluation_result)

    print(json.dumps(evaluation_result, indent=2))
    print(f"\nSaved report to: {REPORT_OUTPUT_PATH}")