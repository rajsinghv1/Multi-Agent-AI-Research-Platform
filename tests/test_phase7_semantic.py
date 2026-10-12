import numpy as np
import pytest

from app.memory import database
from app.memory import semantic_memory


@pytest.fixture
def memory_environment(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DB_PATH",
        tmp_path / "test_memory.db",
    )

    monkeypatch.setattr(
        semantic_memory,
        "MEMORY_DIR",
        tmp_path / "semantic",
    )

    monkeypatch.setattr(
        semantic_memory,
        "INDEX_PATH",
        tmp_path / "semantic" / "memory.index",
    )

    monkeypatch.setattr(
        semantic_memory,
        "META_PATH",
        tmp_path / "semantic" / "memory.json",
    )

    monkeypatch.setattr(
        semantic_memory,
        "embed_documents",
        lambda texts: [[1.0, 0.0, 0.0] for _ in texts],
    )

    monkeypatch.setattr(
        semantic_memory,
        "embed_query",
        lambda question: [1.0, 0.0, 0.0],
    )

    database.init_database()


def test_empty_memory(memory_environment):
    assert semantic_memory.search_memory("RAG") == []


def test_add_memory(memory_environment):
    research_id = database.save_research(
        question="What is RAG?",
        report="RAG combines retrieval and generation.",
    )

    result = semantic_memory.add_research_to_memory(research_id)

    assert result["status"] == "indexed"
    assert result["total_memories"] == 1


def test_duplicate_memory(memory_environment):
    research_id = database.save_research(
        question="Explain FAISS",
        report="FAISS is used for vector similarity search.",
    )

    semantic_memory.add_research_to_memory(research_id)
    result = semantic_memory.add_research_to_memory(research_id)

    assert result["status"] == "already_indexed"


def test_semantic_search(memory_environment):
    research_id = database.save_research(
        question="Explain Retrieval-Augmented Generation",
        report="RAG combines retrieval with language generation.",
    )

    semantic_memory.add_research_to_memory(research_id)

    results = semantic_memory.search_memory("How does RAG work?")

    assert len(results) == 1
    assert results[0]["research_id"] == research_id
    assert results[0]["similarity"] == pytest.approx(1.0)


def test_memory_stats(memory_environment):
    research_id = database.save_research(
        question="Explain LangGraph",
        report="LangGraph orchestrates stateful agents.",
    )

    semantic_memory.add_research_to_memory(research_id)

    stats = semantic_memory.get_memory_stats()

    assert stats["total_memories"] == 1
    assert stats["embedding_dimensions"] == 3


def test_missing_research(memory_environment):
    with pytest.raises(ValueError):
        semantic_memory.add_research_to_memory(999999)


def test_normalization():
    vector = semantic_memory._normalize([3.0, 4.0])

    assert vector.shape == (1, 2)
    assert np.linalg.norm(vector[0]) == pytest.approx(1.0)