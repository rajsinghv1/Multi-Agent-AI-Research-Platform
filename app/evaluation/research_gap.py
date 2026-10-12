
import re

from app.evaluation.quality_scorer import (
    calculate_structure_score,
    extract_citations,
)

GAP_PATTERNS = {
    "insufficient_evidence": [
        r"\bmore research is needed\b",
        r"\blimited evidence\b",
        r"\binsufficient evidence\b",
        r"\black of evidence\b",
        r"\bdoes not extensively cover\b",
        r"\bnot extensively covered\b",
        r"\bprovided evidence does not\b",
    ],
    "unanswered_question": [
        r"\bremains unclear\b",
        r"\bremains unknown\b",
        r"\bopen question\b",
        r"\bnot yet understood\b",
        r"\bdoes not delve into\b",
        r"\bnot fully understood\b",
    ],
    "methodological_limitation": [
        r"\bsmall sample size\b",
        r"\bselection bias\b",
        r"\bnot evaluated\b",
        r"\bnot tested\b",
        r"\bno baseline\b",
        r"\bhighly dependent on\b",
        r"\bhighly contingent on\b",
        r"\btask-dependent\b",
        r"\brequires careful tuning\b",
    ],
    "future_research": [
        r"\bfuture research\b",
        r"\bfuture studies\b",
        r"\bfurther investigation\b",
        r"\bfurther evaluation\b",
        r"\bpotential challenges\b",
        r"\bstrategies to mitigate\b",
    ],
}


def split_sentences(text):
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    text = re.sub(r"\s+", " ", text.strip())

    return [
        sentence.strip()
        for sentence in re.split(
            r"(?<=[.!?])\s+", text
        )
        if sentence.strip()
    ]


def identify_explicit_gaps(report):
    """
    Identify sentences containing research gap indicators.
    """
    gaps = []
    seen = set()

    for sentence in split_sentences(report):
        for category, patterns in GAP_PATTERNS.items():
            if any(
                re.search(pattern, sentence, re.I)
                for pattern in patterns
            ):
                key = (category, sentence.lower())

                if key not in seen:
                    gaps.append({
                        "category": category,
                        "evidence": sentence,
                        "method": "keyword_pattern",
                    })
                    seen.add(key)

    return gaps


def identify_missing_sections(report):
    result = calculate_structure_score(report)
    return result["missing_sections"]


def identify_citation_gaps(report):
    """
    Check whether a report has citations.
    Does not validate individual factual claims.
    """
    citations = extract_citations(report)

    return {
        "has_citations": bool(citations),
        "total_citations": len(citations),
        "unique_citations": len(set(citations)),
        "missing_citations": len(citations) == 0,
    }


def generate_research_questions(gaps):
    """
    Generate follow-up questions from explicit gap evidence.
    """
    questions = []
    seen = set()

    templates = {
        "insufficient_evidence":
            "What additional evidence is needed to address: {}?",
        "unanswered_question":
            "What research could resolve the uncertainty in: {}?",
        "methodological_limitation":
            "How can future studies overcome: {}?",
        "future_research":
            "How should researchers investigate: {}?",
    }

    for gap in gaps:
        category = gap["category"]
        evidence = gap["evidence"].rstrip(".!? ")

        template = templates.get(category)

        if template:
            question = template.format(evidence)

            if question not in seen:
                questions.append(question)
                seen.add(question)

    return questions


def analyze_research_gaps(report):
    """
    Main offline research gap analysis.
    """
    if not isinstance(report, str):
        raise TypeError("Report must be a string.")

    explicit_gaps = identify_explicit_gaps(report)
    missing_sections = identify_missing_sections(report)
    citation_analysis = identify_citation_gaps(report)

    recommendations = []

    if missing_sections:
        recommendations.append(
            "Add missing report sections: "
            + ", ".join(missing_sections)
        )

    if citation_analysis["missing_citations"]:
        recommendations.append(
            "Add verifiable citations supporting research claims."
        )

    if explicit_gaps:
        recommendations.append(
            "Investigate the explicitly identified research gaps."
        )

    questions = generate_research_questions(
        explicit_gaps
    )

    return {
        "total_explicit_gaps": len(explicit_gaps),
        "explicit_gaps": explicit_gaps,
        "missing_sections": missing_sections,
        "citation_analysis": citation_analysis,
        "research_questions": questions,
        "recommendations": recommendations,
        "method": "rule_based_gap_analysis",
    }
