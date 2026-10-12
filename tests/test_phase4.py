from app.services.source_ranker import (
    deduplicate_sources,
    filter_and_rank,
)

from app.services.citation_validator import (
    validate_citations,
)

from app.services.research_cache import (
    get_cached,
    save_cache,
)

from app.services.quality_metrics import (
    calculate_quality_metrics,
)


def sample_sources():
    return [
        {
            "source": "arxiv",
            "title": "Retrieval Augmented Generation",
            "summary": (
                "Retrieval augmented generation combines "
                "search with language models."
            ),
            "url": "https://arxiv.org/abs/1234.5678",
        },
        {
            "source": "arxiv",
            "title": "Retrieval Augmented Generation",
            "summary": "Duplicate research paper.",
            "url": "https://arxiv.org/abs/1234.5678",
        },
        {
            "source": "wikipedia",
            "title": "Marvel Cinematic Universe",
            "summary": "Superhero films and characters.",
            "url": "https://en.wikipedia.org/wiki/Marvel",
        },
    ]


def test_deduplication():
    unique = deduplicate_sources(sample_sources())
    assert len(unique) == 2


def test_relevance_filtering():
    ranked = filter_and_rank(
        "retrieval augmented generation",
        sample_sources(),
        threshold=0.08,
    )

    assert len(ranked) >= 1

    assert all(
        "Marvel" not in source["title"]
        for source in ranked
    )


def test_citation_validation():
    sources = sample_sources()[:2]

    result = validate_citations(
        "Evidence [S1] and invalid source [S9]",
        sources,
    )

    assert result["valid_citations"] == [1]
    assert result["invalid_citations"] == [9]
    assert result["passed"] is False


def test_research_cache(tmp_path, monkeypatch):
    import app.services.research_cache as cache

    monkeypatch.setattr(
        cache,
        "DB_PATH",
        tmp_path / "test_cache.db",
    )

    query = "phase4 test query"
    payload = {"sources": [{"title": "Test"}]}

    save_cache(query, payload)

    assert get_cached(query) == payload


def test_quality_metrics():
    raw = sample_sources()

    ranked = [
        {
            **raw[0],
            "relevance_score": 0.85,
        }
    ]

    metrics = calculate_quality_metrics(
        raw, ranked
    )

    assert metrics["raw_source_count"] == 3
    assert metrics["retained_source_count"] == 1
    assert metrics["filtered_count"] == 2
    assert metrics["average_relevance"] == 0.85