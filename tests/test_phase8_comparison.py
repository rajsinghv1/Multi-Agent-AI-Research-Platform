
import pytest

from app.evaluation.report_comparison import (
    extract_keywords,
    calculate_report_similarity,
    compare_reports,
)


REPORT_A = """
# Introduction
Retrieval augmented generation improves factual accuracy.
External documents provide supporting evidence [D1].

# Conclusion
Retrieval helps language models generate grounded answers.
"""

REPORT_B = """
# Introduction
Retrieval augmented generation improves answer quality.
External documents provide relevant knowledge [D2].

# Conclusion
Retrieval supports grounded language model responses.
"""


def test_extract_keywords():
    result = extract_keywords(REPORT_A)
    assert "retrieval" in result


def test_identical_similarity():
    score = calculate_report_similarity(
        REPORT_A, REPORT_A
    )
    assert score == 100


def test_empty_similarity():
    assert calculate_report_similarity("", "") == 0


def test_similarity_range():
    score = calculate_report_similarity(
        REPORT_A, REPORT_B
    )
    assert 0 <= score <= 100


def test_shared_keywords():
    result = compare_reports(REPORT_A, REPORT_B)
    assert "retrieval" in result["shared_keywords"]


def test_unique_keywords():
    result = compare_reports(REPORT_A, REPORT_B)
    assert "accuracy" in result["unique_to_a"]


def test_quality_comparison():
    result = compare_reports(REPORT_A, REPORT_B)
    assert "quality_comparison" in result


def test_invalid_report():
    with pytest.raises(TypeError):
        compare_reports(None, REPORT_B)


def test_invalid_second_report():
    with pytest.raises(TypeError):
        compare_reports(REPORT_A, None)
