
import pytest

from app.evaluation.source_credibility import (
    evaluate_source,
    rank_sources,
    summarize_sources,
)


def test_peer_reviewed_source():
    result = evaluate_source(
        {"type": "peer_reviewed"},
        current_year=2026,
    )
    assert result["credibility_score"] == 90


def test_unknown_source():
    result = evaluate_source({}, current_year=2026)
    assert result["rating"] == "LOW"


def test_metadata_bonus():
    result = evaluate_source(
        {
            "type": "academic_preprint",
            "title": "Research Paper",
            "author": "Researcher",
            "url": "https://arxiv.org/abs/example",
        },
        current_year=2026,
    )
    assert result["credibility_score"] == 78


def test_recent_publication():
    result = evaluate_source(
        {"type": "news", "year": 2025},
        current_year=2026,
    )
    assert result["credibility_score"] == 65


def test_old_publication():
    result = evaluate_source(
        {"type": "news", "year": 2000},
        current_year=2026,
    )
    assert result["credibility_score"] == 55


def test_future_publication():
    result = evaluate_source(
        {"type": "blog", "year": 2030},
        current_year=2026,
    )
    assert result["credibility_score"] == 30


def test_valid_doi():
    result = evaluate_source(
        {
            "type": "academic_preprint",
            "doi": "10.1234/example",
        },
        current_year=2026,
    )
    assert result["credibility_score"] == 75


def test_rank_sources():
    ranked = rank_sources(
        [
            {"type": "blog"},
            {"type": "peer_reviewed"},
            {"type": "news"},
        ],
        current_year=2026,
    )
    assert ranked[0]["source_type"] == "peer_reviewed"


def test_empty_summary():
    result = summarize_sources([])
    assert result["total_sources"] == 0


def test_source_summary():
    result = summarize_sources(
        [
            {"type": "peer_reviewed"},
            {"type": "blog"},
        ],
        current_year=2026,
    )
    assert result["total_sources"] == 2
    assert result["high"] == 1
    assert result["low"] == 1


def test_invalid_source():
    with pytest.raises(TypeError):
        evaluate_source("invalid")


def test_invalid_sources_list():
    with pytest.raises(TypeError):
        rank_sources("invalid")
