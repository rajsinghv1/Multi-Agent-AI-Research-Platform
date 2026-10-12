
from datetime import datetime, timezone
from urllib.parse import urlparse
import re


SOURCE_TYPES = {
    "peer_reviewed": 90,
    "academic_preprint": 70,
    "official_documentation": 85,
    "government": 85,
    "news": 60,
    "blog": 40,
    "unknown": 30,
}


def normalize_source_type(source_type):
    value = str(source_type or "unknown").strip().lower()
    return value if value in SOURCE_TYPES else "unknown"


def evaluate_source(source, current_year=None):
    """
    Evaluate source metadata using transparent heuristics.

    Does not verify factual correctness, publisher
    reputation, or whether peer review actually occurred.
    """
    if not isinstance(source, dict):
        raise TypeError("Source must be a dictionary.")

    current_year = (
        current_year
        if current_year is not None
        else datetime.now(timezone.utc).year
    )

    source_type = normalize_source_type(
        source.get("type")
    )

    base_score = SOURCE_TYPES[source_type]
    score = float(base_score)

    reasons = [
        f"Source type: {source_type}"
    ]

    title = str(source.get("title") or "").strip()
    url = str(source.get("url") or "").strip()
    author = str(source.get("author") or "").strip()
    year = source.get("year")
    doi = str(source.get("doi") or "").strip()

    if title:
        score += 2
        reasons.append("Title provided")

    if author:
        score += 3
        reasons.append("Author provided")

    if doi and re.fullmatch(
        r"10\.\d{4,9}/\S+", doi
    ):
        score += 5
        reasons.append("DOI format is valid")

    parsed_url = urlparse(url)

    if parsed_url.scheme == "https" and parsed_url.netloc:
        score += 3
        reasons.append("HTTPS URL provided")

    if year is not None:
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = None

        if year is not None:
            age = current_year - year

            if age < 0:
                reasons.append("Future publication year")
                score -= 10
            elif age <= 2:
                score += 5
                reasons.append("Recent publication")
            elif age <= 5:
                score += 2
                reasons.append("Relatively recent publication")
            elif age > 15:
                score -= 5
                reasons.append("Older publication")

    score = round(max(0, min(100, score)), 2)

    if score >= 85:
        rating = "HIGH"
    elif score >= 60:
        rating = "MODERATE"
    else:
        rating = "LOW"

    return {
        "title": title,
        "url": url,
        "source_type": source_type,
        "credibility_score": score,
        "rating": rating,
        "reasons": reasons,
        "method": "metadata_heuristic",
    }


def rank_sources(sources, current_year=None):
    if not isinstance(sources, list):
        raise TypeError("Sources must be a list.")

    evaluated = [
        evaluate_source(source, current_year)
        for source in sources
    ]

    return sorted(
        evaluated,
        key=lambda item: item["credibility_score"],
        reverse=True,
    )


def summarize_sources(sources, current_year=None):
    ranked = rank_sources(sources, current_year)

    if not ranked:
        return {
            "total_sources": 0,
            "average_score": 0,
            "high": 0,
            "moderate": 0,
            "low": 0,
            "ranked_sources": [],
        }

    return {
        "total_sources": len(ranked),
        "average_score": round(
            sum(s["credibility_score"] for s in ranked)
            / len(ranked),
            2,
        ),
        "high": sum(s["rating"] == "HIGH" for s in ranked),
        "moderate": sum(s["rating"] == "MODERATE" for s in ranked),
        "low": sum(s["rating"] == "LOW" for s in ranked),
        "ranked_sources": ranked,
    }
