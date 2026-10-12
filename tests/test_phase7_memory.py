import pytest

from app.memory import database


@pytest.fixture
def temporary_database(tmp_path, monkeypatch):
    test_db = tmp_path / "test_research_memory.db"

    monkeypatch.setattr(database, "DB_PATH", test_db)

    database.init_database()

    return test_db


def test_save_research(temporary_database):
    research_id = database.save_research(
        question="What is RAG?",
        report="RAG combines retrieval with generation.",
    )

    assert research_id > 0


def test_get_research(temporary_database):
    research_id = database.save_research(
        question="What is LangGraph?",
        report="LangGraph orchestrates stateful workflows.",
        evidence=[
            {"citation_id": "S1", "title": "Example Paper"}
        ],
    )

    result = database.get_research(research_id)

    assert result["question"] == "What is LangGraph?"
    assert result["evidence"][0]["citation_id"] == "S1"


def test_list_research(temporary_database):
    database.save_research(
        question="Explain FAISS",
        report="FAISS supports vector similarity search.",
    )

    history = database.list_research()

    assert len(history) == 1
    assert history[0]["question"] == "Explain FAISS"


def test_search_research(temporary_database):
    database.save_research(
        question="Explain Retrieval-Augmented Generation",
        report="RAG combines retrieval and generation.",
    )

    results = database.search_research("Retrieval")

    assert len(results) == 1


def test_delete_research(temporary_database):
    research_id = database.save_research(
        question="Temporary research",
        report="Temporary report.",
    )

    assert database.delete_research(research_id) is True
    assert database.get_research(research_id) is None