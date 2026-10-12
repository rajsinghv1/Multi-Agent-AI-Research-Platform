import pytest

from app.evaluation.quality_scorer import (
    extract_citations,
    calculate_structure_score,
    calculate_citation_score,
    calculate_depth_score,
    calculate_readability_score,
    evaluate_research_quality,
)


SAMPLE_REPORT = """
# Executive Summary
RAG improves language model reliability [D1].

# Introduction
Language models may hallucinate [D1].

# Key Findings
Retrieval provides external knowledge [D2].

# Analysis
Retrieved evidence helps ground responses [D2].

# Limitations
Retrieval quality affects results [D3].

# Conclusion
RAG can improve factual grounding [D1].
"""


def test_extract_citations():
    citations = extract_citations(
        "Evidence [D1] and [D2]."
    )

    assert citations == ["D1", "D2"]


def test_structure_score():
    result = calculate_structure_score(
        SAMPLE_REPORT
    )

    assert result["score"] == 100
    assert result["missing_sections"] == []


def test_missing_sections():
    result = calculate_structure_score(
        "# Introduction\nSome text."
    )

    assert result["score"] < 100


def test_citation_score():
    result = calculate_citation_score(
        SAMPLE_REPORT
    )

    assert result["total_citations"] == 6
    assert result["unique_citations"] == 3


def test_no_citations():
    result = calculate_citation_score(
        "This report contains no references."
    )

    assert result["score"] == 0


def test_depth_score():
    result = calculate_depth_score(
        "word " * 1600
    )

    assert result["score"] == 100


def test_readability_score():
    result = calculate_readability_score(
        "RAG retrieves documents. "
        "The model generates answers."
    )

    assert result["score"] > 0


def test_empty_report():
    result = evaluate_research_quality("")

    assert result["overall_score"] == 0
    assert result["grade"] == "NEEDS IMPROVEMENT"


def test_invalid_input():
    with pytest.raises(TypeError):
        evaluate_research_quality(None)


def test_score_range():
    result = evaluate_research_quality(
        SAMPLE_REPORT
    )

    assert 0 <= result["overall_score"] <= 100


def test_recommendations():
    result = evaluate_research_quality(
        "Short report."
    )

    assert len(result["recommendations"]) > 0