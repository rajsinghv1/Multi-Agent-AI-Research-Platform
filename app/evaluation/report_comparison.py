
import re
from difflib import SequenceMatcher

from app.evaluation.quality_scorer import (
    evaluate_research_quality,
)


STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were",
    "and", "or", "of", "to", "in", "on", "for",
    "with", "by", "from", "as", "that", "this",
    "it", "be", "has", "have", "had",
}


def extract_keywords(text, limit=20):
    if not isinstance(text, str):
        raise TypeError("Report must be a string.")

    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())

    frequency = {}

    for word in words:
        if word not in STOPWORDS:
            frequency[word] = frequency.get(word, 0) + 1

    ranked = sorted(
        frequency.items(),
        key=lambda item: (-item[1], item[0]),
    )

    return [word for word, _ in ranked[:limit]]


def calculate_report_similarity(report_a, report_b):
    keywords_a = set(extract_keywords(report_a))
    keywords_b = set(extract_keywords(report_b))

    if not keywords_a or not keywords_b:
        return 0.0

    overlap = len(keywords_a & keywords_b)
    union = len(keywords_a | keywords_b)

    jaccard = overlap / union

    sequence = SequenceMatcher(
        None,
        " ".join(sorted(keywords_a)),
        " ".join(sorted(keywords_b)),
    ).ratio()

    return round(
        (0.7 * jaccard + 0.3 * sequence) * 100,
        2,
    )


def compare_reports(report_a, report_b):
    if not isinstance(report_a, str):
        raise TypeError("First report must be a string.")

    if not isinstance(report_b, str):
        raise TypeError("Second report must be a string.")

    keywords_a = set(extract_keywords(report_a))
    keywords_b = set(extract_keywords(report_b))

    quality_a = evaluate_research_quality(report_a)
    quality_b = evaluate_research_quality(report_b)

    return {
        "similarity_score": calculate_report_similarity(
            report_a, report_b
        ),
        "shared_keywords": sorted(
            keywords_a & keywords_b
        ),
        "unique_to_a": sorted(
            keywords_a - keywords_b
        ),
        "unique_to_b": sorted(
            keywords_b - keywords_a
        ),
        "quality_comparison": {
            "report_a_score": quality_a["overall_score"],
            "report_b_score": quality_b["overall_score"],
            "score_difference": round(
                quality_a["overall_score"]
                - quality_b["overall_score"],
                2,
            ),
            "report_a_grade": quality_a["grade"],
            "report_b_grade": quality_b["grade"],
        },
        "method": "keyword_overlap_heuristic",
    }
