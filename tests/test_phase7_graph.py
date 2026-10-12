import pytest

from app.memory import database
from app.memory import knowledge_graph as kg


@pytest.fixture
def graph_database(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DB_PATH",
        tmp_path / "graph_test.db",
    )

    database.init_database()
    kg.init_knowledge_graph()


def test_add_entity(graph_database):
    entity_id = kg.add_entity("FAISS", "TOOL")

    assert entity_id > 0


def test_duplicate_entity(graph_database):
    first = kg.add_entity("FAISS", "TOOL")
    second = kg.add_entity("faiss", "TOOL")

    assert first == second
    assert kg.get_graph_stats()["entities"] == 1


def test_add_relationship(graph_database):
    kg.add_relationship("RAG", "USES", "FAISS")

    relationships = kg.get_relationships("RAG")

    assert len(relationships) == 1
    assert relationships[0]["target"] == "FAISS"


def test_save_extraction(graph_database):
    extraction = {
        "entities": [
            {"name": "RAG", "type": "TECHNIQUE"},
            {"name": "FAISS", "type": "TOOL"},
        ],
        "relationships": [
            {
                "source": "RAG",
                "relation": "USES",
                "target": "FAISS",
            }
        ],
    }

    kg.save_extraction(extraction)

    stats = kg.get_graph_stats()

    assert stats["entities"] == 2
    assert stats["relationships"] == 1


def test_graph_query(graph_database):
    kg.add_relationship("LangGraph", "ORCHESTRATES", "Agents")
    kg.add_relationship("RAG", "USES", "FAISS")

    result = kg.get_relationships("LangGraph")

    assert len(result) == 1
    assert result[0]["relation"] == "ORCHESTRATES"


def test_graph_stats(graph_database):
    kg.add_entity("Gemini", "MODEL")
    kg.add_entity("FAISS", "TOOL")

    stats = kg.get_graph_stats()

    assert stats["entities"] == 2
    assert stats["relationships"] == 0