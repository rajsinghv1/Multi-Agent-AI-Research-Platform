from app.memory import database
from app.memory import knowledge_graph
from app.memory import recover_graph


def test_recover_graph(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DB_PATH",
        tmp_path / "recovery.db",
    )

    research_id = database.save_research(
        question="What is RAG?",
        report="RAG uses FAISS for vector retrieval.",
    )

    monkeypatch.setattr(
        recover_graph,
        "extract_entities_and_relationships",
        lambda text: {
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
        },
    )

    result = recover_graph.recover_knowledge_graph(
        research_id
    )

    assert len(result["entities"]) == 2
    assert len(result["relationships"]) == 1

    stats = knowledge_graph.get_graph_stats()

    assert stats["entities"] == 2
    assert stats["relationships"] == 1