import re
from collections import Counter


REQUIRED_SECTIONS = {
    "executive_summary": [
        "executive summary",
        "abstract",
    ],
    "introduction": [
        "introduction",
        "background",
    ],
    "findings": [
        "key findings",
        "results",
        "findings",
    ],
    "analysis": [
        "analysis",
        "discussion",
        "comparative analysis",
    ],
    "limitations": [
        "limitations",
        "research limitations",
    ],
    "conclusion": [
        "conclusion",
        "conclusions",
    ],
}


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def extract_citations(report):
    """
    Extract citations such as:
    [D1], [D2], [W1], [S3]
    """
    return re.findall(
        r"\[([A-Za-z]+\d+)\]",
        report,
    )


def calculate_structure_score(report):
    """
    Score research structure out of 100.
    """
    text = report.lower()

    found = []

    for section, keywords in REQUIRED_SECTIONS.items():
        if any(keyword in text for keyword in keywords):
            found.append(section)

    score = (
        len(found) / len(REQUIRED_SECTIONS)
    ) * 100

    return {
        "score": round(score, 2),
        "found_sections": found,
        "missing_sections": [
            section
            for section in REQUIRED_SECTIONS
            if section not in found
        ],
    }


def calculate_citation_score(report):
    """
    Heuristic citation score based on:
    - Citation count
    - Unique citations
    - Citation distribution
    """
    citations = extract_citations(report)

    if not citations:
        return {
            "score": 0,
            "total_citations": 0,
            "unique_citations": 0,
            "citation_frequency": {},
        }

    unique = set(citations)
    words = max(len(report.split()), 1)

    citation_density = (
        len(citations) / words
    ) * 1000

    density_score = clamp(
        citation_density * 10
    )

    diversity_score = clamp(
        len(unique) * 20
    )

    score = (
        density_score * 0.6
        + diversity_score * 0.4
    )

    return {
        "score": round(score, 2),
        "total_citations": len(citations),
        "unique_citations": len(unique),
        "citation_frequency": dict(
            Counter(citations)
        ),
    }


def calculate_depth_score(report):
    """
    Approximate research depth using report length.
    """
    words = len(report.split())

    if words >= 1500:
        score = 100
    elif words >= 1000:
        score = 85
    elif words >= 600:
        score = 70
    elif words >= 300:
        score = 50
    elif words >= 100:
        score = 30
    else:
        score = 10 if words else 0

    return {
        "score": score,
        "word_count": words,
    }


def calculate_readability_score(report):
    """
    Simple readability heuristic.
    Not a formal readability grade.
    """
    words = re.findall(r"\b\w+\b", report)

    if not words:
        return {
            "score": 0,
            "average_sentence_length": 0,
        }

    sentences = [
        sentence.strip()
        for sentence in re.split(
            r"[.!?]+",
            report,
        )
        if sentence.strip()
    ]

    average_length = (
        len(words) / max(len(sentences), 1)
    )

    if average_length <= 15:
        score = 100
    elif average_length <= 25:
        score = 85
    elif average_length <= 35:
        score = 65
    elif average_length <= 45:
        score = 45
    else:
        score = 25

    return {
        "score": score,
        "average_sentence_length": round(
            average_length, 2
        ),
    }


def evaluate_research_quality(report):
    """
    Main research quality evaluation.

    Returns overall score and breakdown.
    """
    if not isinstance(report, str):
        raise TypeError("Report must be a string.")

    structure = calculate_structure_score(report)
    citations = calculate_citation_score(report)
    depth = calculate_depth_score(report)
    readability = calculate_readability_score(report)

    weights = {
        "structure": 0.30,
        "citations": 0.30,
        "depth": 0.25,
        "readability": 0.15,
    }

    overall = (
        structure["score"] * weights["structure"]
        + citations["score"] * weights["citations"]
        + depth["score"] * weights["depth"]
        + readability["score"] * weights["readability"]
    )

    overall = round(clamp(overall), 2)

    if overall >= 85:
        grade = "EXCELLENT"
    elif overall >= 70:
        grade = "GOOD"
    elif overall >= 50:
        grade = "AVERAGE"
    else:
        grade = "NEEDS IMPROVEMENT"

    recommendations = []

    if structure["score"] < 100:
        recommendations.append(
            "Add missing research sections."
        )

    if citations["score"] < 70:
        recommendations.append(
            "Improve citation coverage and diversity."
        )

    if depth["score"] < 70:
        recommendations.append(
            "Expand the research with deeper analysis."
        )

    if readability["score"] < 70:
        recommendations.append(
            "Improve readability by shortening sentences."
        )

    return {
        "overall_score": overall,
        "grade": grade,
        "weights": weights,
        "structure": structure,
        "citations": citations,
        "depth": depth,
        "readability": readability,
        "recommendations": recommendations,
    }