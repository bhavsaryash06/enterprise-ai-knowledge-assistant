import json
import re
from pathlib import Path
from typing import Any

from app.graph.workflow import run_rag_workflow


EVAL_DATASET_PATH = Path("app/evaluation/eval_dataset.json")
REPORT_OUTPUT_PATH = Path("app/evaluation/answer_eval_report.json")


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "may",
    "must",
    "of",
    "or",
    "should",
    "the",
    "to",
    "with",
}


def load_eval_dataset() -> list[dict[str, Any]]:
    with open(EVAL_DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def get_keywords(text: str) -> set[str]:
    normalized_text = normalize_text(text)
    words = normalized_text.split()

    return {
        word
        for word in words
        if word not in STOPWORDS and len(word) > 2
    }


def calculate_answer_point_match(
    answer: str,
    expected_answer_points: list[str],
) -> dict[str, Any]:
    answer_keywords = get_keywords(answer)

    matched_points = []
    missed_points = []

    for point in expected_answer_points:
        point_keywords = get_keywords(point)

        if not point_keywords:
            missed_points.append(point)
            continue

        overlap = answer_keywords.intersection(point_keywords)
        overlap_ratio = len(overlap) / len(point_keywords)

        if overlap_ratio >= 0.5:
            matched_points.append(point)
        else:
            missed_points.append(point)

    if not expected_answer_points:
        match_rate = 1.0
    else:
        match_rate = len(matched_points) / len(expected_answer_points)

    return {
        "matched_points": matched_points,
        "missed_points": missed_points,
        "answer_point_match_rate": match_rate,
    }


def get_source_document_names(sources: list[dict[str, Any]]) -> list[str]:
    document_names = []

    for source in sources:
        document_name = source.get("document_name")

        if document_name and document_name not in document_names:
            document_names.append(document_name)

    return document_names


def evaluate_single_answer(item: dict[str, Any]) -> dict[str, Any]:
    question = item["question"]
    expected_behavior = item["expected_behavior"]
    should_escalate = item["should_escalate"]
    expected_answer_points = item["expected_answer_points"]

    result = run_rag_workflow(
        question=question,
        top_k=5,
        use_query_rewrite=True,
        use_reranking=True,
        document_type="Policy",
    )

    answer = result.get("answer", "")
    escalation_required = result.get("escalation_required", False)
    confidence = result.get("confidence", "unknown")
    sources = result.get("sources", [])

    behavior_correct = escalation_required == should_escalate

    answer_point_result = calculate_answer_point_match(
        answer=answer,
        expected_answer_points=expected_answer_points,
    )

    source_document_names = get_source_document_names(sources)

    if expected_behavior == "answer":
        passed = (
            behavior_correct
            and answer_point_result["answer_point_match_rate"] >= 0.5
            and len(source_document_names) > 0
        )
    else:
        passed = behavior_correct

    return {
        "id": item["id"],
        "question": question,
        "category": item["category"],
        "expected_behavior": expected_behavior,
        "should_escalate": should_escalate,
        "actual_escalation_required": escalation_required,
        "behavior_correct": behavior_correct,
        "confidence": confidence,
        "answer_point_match_rate": answer_point_result["answer_point_match_rate"],
        "matched_points": answer_point_result["matched_points"],
        "missed_points": answer_point_result["missed_points"],
        "source_documents": source_document_names,
        "answer_preview": answer[:500],
        "passed": passed,
    }


def run_answer_evaluation() -> dict[str, Any]:
    dataset = load_eval_dataset()

    results = []
    supported_results = []
    unsupported_results = []

    for item in dataset:
        try:
            result = evaluate_single_answer(item)
            results.append(result)

            if item["expected_behavior"] == "answer":
                supported_results.append(result)
            else:
                unsupported_results.append(result)

        except Exception as error:
            results.append(
                {
                    "id": item["id"],
                    "question": item["question"],
                    "category": item["category"],
                    "expected_behavior": item["expected_behavior"],
                    "passed": False,
                    "error": str(error),
                }
            )

    total_questions = len(results)
    passed_count = len([result for result in results if result.get("passed") is True])
    failed_count = total_questions - passed_count

    behavior_correct_count = len(
        [result for result in results if result.get("behavior_correct") is True]
    )

    supported_pass_count = len(
        [result for result in supported_results if result.get("passed") is True]
    )

    unsupported_pass_count = len(
        [result for result in unsupported_results if result.get("passed") is True]
    )

    average_answer_point_match_rate = (
        sum(
            result.get("answer_point_match_rate", 0.0)
            for result in supported_results
        )
        / len(supported_results)
        if supported_results
        else 0.0
    )

    report = {
        "total_questions": total_questions,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "behavior_accuracy": behavior_correct_count / total_questions if total_questions else 0.0,
        "supported_questions": len(supported_results),
        "supported_pass_count": supported_pass_count,
        "unsupported_questions": len(unsupported_results),
        "unsupported_pass_count": unsupported_pass_count,
        "average_answer_point_match_rate": average_answer_point_match_rate,
        "results": results,
    }

    return report


def save_report(report: dict[str, Any]) -> None:
    REPORT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


if __name__ == "__main__":
    evaluation_result = run_answer_evaluation()
    save_report(evaluation_result)

    print(json.dumps(evaluation_result, indent=2))
    print(f"\nSaved report to: {REPORT_OUTPUT_PATH}")