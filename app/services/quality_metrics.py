from statistics import mean


def calculate_quality_metrics(
    raw_sources,
    ranked_sources,
    errors=None
):
    errors = errors or []

    scores = [
        source.get("relevance_score", 0.0)
        for source in ranked_sources
    ]

    providers = {
        source.get("source", "unknown")
        for source in ranked_sources
    }

    return {
        "raw_source_count": len(raw_sources),
        "retained_source_count": len(ranked_sources),
        "filtered_count": (
            len(raw_sources) - len(ranked_sources)
        ),
        "average_relevance": round(
            mean(scores), 4
        ) if scores else 0.0,
        "source_diversity": len(providers),
        "providers": sorted(providers),
        "retrieval_error_count": len(errors)
    }