
import pytest

from app.evaluation.research_gap import (
    split_sentences,
    identify_explicit_gaps,
    identify_missing_sections,
    identify_citation_gaps,
    generate_research_questions,
    analyze_research_gaps,
)


SAMPLE_REPORT = """
# Executive Summary
RAG improves factual grounding [D1].

# Introduction
Retrieval provides external context [D1].

# Key Findings
Some results remain unclear.

# Analysis
Limited evidence exists for multilingual settings.

# Limitations
The system was not evaluated on medical data.

# Conclusion
Future research should investigate domain transfer.
"""


def test_sentence_split():
    result = split_sentences(
        "First finding. Second finding."
    )
    assert len(result) == 2


def test_explicit_gaps():
    result = identify_explicit_gaps(SAMPLE_REPORT)
    assert len(result) >= 3


def test_unanswered_question():
    result = identify_explicit_gaps(
        "The impact remains unclear."
    )
    assert result[0]["category"] == "unanswered_question"


def test_insufficient_evidence():
    result = identify_explicit_gaps(
        "Limited evidence exists for this method."
    )
    assert result[0]["category"] == "insufficient_evidence"


def test_methodological_gap():
    result = identify_explicit_gaps(
        "The approach was not tested on real data."
    )
    assert result[0]["category"] == "methodological_limitation"


def test_future_research():
    result = identify_explicit_gaps(
        "Future research should evaluate the model."
    )
    assert result[0]["category"] == "future_research"


def test_missing_sections():
    result = identify_missing_sections(
        "# Introduction\nSome research."
    )
    assert "conclusion" in result


def test_citations_present():
    result = identify_citation_gaps(
        "Evidence [D1] and [D2]."
    )
    assert result["total_citations"] == 2


def test_missing_citations():
    result = identify_citation_gaps(
        "Research without references."
    )
    assert result["missing_citations"] is True


def test_generate_questions():
    gaps = identify_explicit_gaps(
        "The outcome remains unclear."
    )
    questions = generate_research_questions(gaps)
    assert len(questions) == 1


def test_full_analysis():
    result = analyze_research_gaps(SAMPLE_REPORT)
    assert result["total_explicit_gaps"] >= 3
    assert len(result["research_questions"]) >= 3


def test_empty_report():
    result = analyze_research_gaps("")
    assert result["total_explicit_gaps"] == 0
    assert result["citation_analysis"]["missing_citations"]


def test_invalid_input():
    with pytest.raises(TypeError):
        analyze_research_gaps(None)
