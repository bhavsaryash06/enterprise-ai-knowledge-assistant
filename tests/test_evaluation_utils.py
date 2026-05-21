from app.evaluation.answer_eval import calculate_answer_point_match
from app.evaluation.retrieval_eval import (
    calculate_source_recall,
    get_result_status,
)


def test_calculate_source_recall_full_match():
    expected_sources = [
        "Finance Reimbursement Policy V1",
        "Remote Work Policy V1",
    ]

    retrieved_sources = [
        "Finance Reimbursement Policy V1",
        "Remote Work Policy V1",
        "Travel And Expense Policy V1",
    ]

    result = calculate_source_recall(
        expected_sources=expected_sources,
        retrieved_sources=retrieved_sources,
    )

    assert result["source_recall"] == 1.0
    assert len(result["matched_sources"]) == 2


def test_calculate_source_recall_partial_match():
    expected_sources = [
        "Device Usage Policy V1",
        "Incident Reporting Sop V1",
        "It Security Policy V1",
    ]

    retrieved_sources = [
        "Device Usage Policy V1",
        "Incident Reporting Sop V1",
    ]

    result = calculate_source_recall(
        expected_sources=expected_sources,
        retrieved_sources=retrieved_sources,
    )

    assert result["source_recall"] == 2 / 3
    assert len(result["matched_sources"]) == 2


def test_calculate_source_recall_unsupported_question_returns_none():
    result = calculate_source_recall(
        expected_sources=[],
        retrieved_sources=["Finance Reimbursement Policy V1"],
    )

    assert result["source_recall"] is None
    assert result["matched_sources"] == []


def test_get_result_status_pass():
    status = get_result_status(
        expected_behavior="answer",
        source_recall=1.0,
    )

    assert status == "pass"


def test_get_result_status_partial():
    status = get_result_status(
        expected_behavior="answer",
        source_recall=0.5,
    )

    assert status == "partial"


def test_get_result_status_unsupported():
    status = get_result_status(
        expected_behavior="escalate",
        source_recall=None,
    )

    assert status == "unsupported_not_scored_for_retrieval"


def test_answer_point_match_rate():
    answer = (
        "Yes, a home office monitor may be reimbursable. "
        "Manager approval is required before purchase. "
        "The reimbursement limit is USD 250."
    )

    expected_points = [
        "home office monitor may be reimbursable",
        "manager approval is required before purchase",
        "monitor reimbursement limit applies",
    ]

    result = calculate_answer_point_match(
        answer=answer,
        expected_answer_points=expected_points,
    )

    assert result["answer_point_match_rate"] >= 0.66
    assert len(result["matched_points"]) >= 2


def test_unsupported_answer_point_match_rate():
    answer = (
        "I could not find strong enough evidence in the company documents "
        "to answer this question confidently. Please escalate this to the appropriate department."
    )

    expected_points = [
        "not enough evidence",
        "cannot answer confidently",
        "escalate to appropriate department",
    ]

    result = calculate_answer_point_match(
        answer=answer,
        expected_answer_points=expected_points,
    )

    assert result["answer_point_match_rate"] == 1.0