
from app.evaluation.quality_scorer import (
    evaluate_research_quality,
)
from app.evaluation.contradiction_detector import (
    analyze_evidence,
)
from app.evaluation.source_credibility import (
    summarize_sources,
)
from app.evaluation.research_gap import (
    analyze_research_gaps,
)
from app.evaluation.report_comparison import (
    compare_reports,
)


def evaluate_research(
    report,
    evidence=None,
    sources=None,
    comparison_report=None,
):
    """
    Unified offline research evaluation.

    Does not call Gemini or other external APIs.
    """

    if not isinstance(report, str):
        raise TypeError("Report must be a string.")

    if evidence is None:
        evidence = []

    if sources is None:
        sources = []

    quality = evaluate_research_quality(report)

    contradictions = analyze_evidence(evidence)

    credibility = summarize_sources(sources)

    gaps = analyze_research_gaps(report)

    comparison = None

    if comparison_report is not None:
        comparison = compare_reports(
            report,
            comparison_report,
        )

    warnings = []

    if quality["overall_score"] < 70:
        warnings.append(
            "Research quality heuristic score is below 70."
        )

    if contradictions["contradictions_found"] > 0:
        warnings.append(
            "Potential contradictory evidence detected."
        )

    if credibility["total_sources"] == 0:
        warnings.append(
            "No source metadata provided for credibility analysis."
        )

    if gaps["total_explicit_gaps"] > 0:
        warnings.append(
            "Research gaps identified for further investigation."
        )

    return {
        "quality": quality,
        "contradictions": contradictions,
        "credibility": credibility,
        "research_gaps": gaps,
        "comparison": comparison,
        "warnings": warnings,
        "evaluation_method": "offline_heuristic_pipeline",
    }
