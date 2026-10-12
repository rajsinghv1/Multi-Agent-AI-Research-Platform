
import pytest

from app.evaluation.contradiction_detector import (
    normalize_text,
    has_negation,
    calculate_similarity,
    detect_contradiction,
    analyze_evidence,
)


def test_normalization():
    result = normalize_text(
        "RAG DOESN'T improve accuracy!"
    )
    assert result == "rag does not improve accuracy"


def test_negation_detection():
    assert has_negation(
        "RAG does not improve accuracy."
    )
    assert not has_negation(
        "RAG improves accuracy."
    )


def test_similarity():
    score = calculate_similarity(
        "RAG improves factual accuracy",
        "RAG improves factual accuracy"
    )
    assert score == 1.0


def test_contradiction():
    result = detect_contradiction(
        "RAG improves factual accuracy.",
        "RAG does not improve factual accuracy."
    )
    assert result["is_contradiction"] is True


def test_no_contradiction():
    result = detect_contradiction(
        "RAG improves accuracy.",
        "RAG improves accuracy."
    )
    assert result["is_contradiction"] is False


def test_unrelated_claims():
    result = detect_contradiction(
        "RAG improves factual accuracy.",
        "Python does not require compilation."
    )
    assert result["is_contradiction"] is False


def test_evidence_analysis():
    evidence = [
        {
            "source": "D1",
            "claim": "RAG improves factual accuracy."
        },
        {
            "source": "D2",
            "claim": "RAG does not improve factual accuracy."
        },
        {
            "source": "D3",
            "claim": "Python supports multiple programming paradigms."
        },
    ]

    result = analyze_evidence(evidence)

    assert result["total_evidence"] == 3
    assert result["checked_pairs"] == 3
    assert result["contradictions_found"] == 1


def test_empty_evidence():
    result = analyze_evidence([])
    assert result["contradictions_found"] == 0


def test_invalid_evidence():
    with pytest.raises(TypeError):
        analyze_evidence("not a list")


def test_missing_claim():
    result = analyze_evidence([
        {"source": "D1"},
        {"source": "D2", "claim": "RAG improves accuracy."},
    ])
    assert result["checked_pairs"] == 0
