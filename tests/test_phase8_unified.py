
import pytest

from app.evaluation.unified_evaluator import (
    evaluate_research,
)


REPORT = """
# Executive Summary
RAG improves factual accuracy [D1].

# Introduction
RAG retrieves external evidence [D1].

# Key Findings
Retrieval supports factual grounding [D2].

# Analysis
Some results remain unclear.

# Limitations
Limited evidence exists for certain domains.

# Conclusion
Future research should evaluate reliability.
"""


def test_unified_evaluation():
    result = evaluate_research(REPORT)

    assert "quality" in result
    assert "contradictions" in result
    assert "credibility" in result
    assert "research_gaps" in result


def test_with_evidence():
    evidence = [
        {
            "source": "D1",
            "claim": "RAG improves factual accuracy.",
        },
        {
            "source": "D2",
            "claim": "RAG does not improve factual accuracy.",
        },
    ]

    result = evaluate_research(
        REPORT,
        evidence=evidence,
    )

    assert (
        result["contradictions"]["contradictions_found"]
        == 1
    )


def test_with_sources():
    sources = [
        {"type": "peer_reviewed"},
        {"type": "academic_preprint"},
    ]

    result = evaluate_research(
        REPORT,
        sources=sources,
    )

    assert result["credibility"]["total_sources"] == 2


def test_with_comparison():
    result = evaluate_research(
        REPORT,
        comparison_report="RAG improves answers.",
    )

    assert result["comparison"] is not None


def test_empty_report():
    result = evaluate_research("")

    assert result["quality"]["overall_score"] == 0


def test_invalid_report():
    with pytest.raises(TypeError):
        evaluate_research(None)


def test_gap_detection():
    result = evaluate_research(REPORT)

    assert (
        result["research_gaps"]["total_explicit_gaps"]
        >= 1
    )


def test_warnings():
    result = evaluate_research("Short report.")

    assert len(result["warnings"]) > 0
