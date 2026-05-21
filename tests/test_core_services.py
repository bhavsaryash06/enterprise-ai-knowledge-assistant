from app.services.chunking_service import split_text_into_chunks
from app.services.evidence_checker import assess_evidence_strength
from app.services.text_cleaner import clean_text


def test_clean_text_removes_extra_spaces_and_blank_lines():
    messy_text = "Hello     world\n\n\n   Policy text here   "

    cleaned = clean_text(messy_text)

    assert cleaned == "Hello world\n\nPolicy text here"


def test_split_text_into_chunks_returns_chunks():
    text = "Employees may request reimbursement for approved equipment. " * 50

    chunks = split_text_into_chunks(
        text=text,
        chunk_size=300,
        chunk_overlap=50,
    )

    assert len(chunks) > 1
    assert chunks[0]["chunk_number"] == 1
    assert "text" in chunks[0]
    assert chunks[0]["text_length"] > 0


def test_split_text_into_chunks_empty_text_returns_empty_list():
    chunks = split_text_into_chunks("   ")

    assert chunks == []


def test_split_text_into_chunks_invalid_overlap_raises_error():
    try:
        split_text_into_chunks(
            text="Some policy text",
            chunk_size=100,
            chunk_overlap=100,
        )
    except ValueError as error:
        assert "chunk_overlap must be smaller than chunk_size" in str(error)
    else:
        assert False, "Expected ValueError was not raised"


def test_evidence_checker_high_confidence():
    retrieved_chunks = [
        {
            "text": "Employees may request reimbursement for approved home office equipment.",
            "score": 0.72,
        }
    ]

    result = assess_evidence_strength(retrieved_chunks)

    assert result["confidence"] == "high"
    assert result["escalation_required"] is False


def test_evidence_checker_low_confidence_when_no_chunks():
    result = assess_evidence_strength([])

    assert result["confidence"] == "low"
    assert result["escalation_required"] is True


def test_evidence_checker_low_confidence_for_weak_score():
    retrieved_chunks = [
        {
            "text": "Unrelated policy text.",
            "score": 0.30,
        }
    ]

    result = assess_evidence_strength(retrieved_chunks)

    assert result["confidence"] == "low"
    assert result["escalation_required"] is True