from app.workflows import memory_graph as module


def test_graph_structure():
    nodes = module.memory_graph.get_graph().nodes

    assert "retrieve_memory" in nodes
    assert "hybrid_research" in nodes
    assert "save_memory" in nodes
    assert "knowledge_graph" in nodes


def test_retrieve_memory(monkeypatch):
    monkeypatch.setattr(
        module,
        "search_memory",
        lambda question, top_k, min_score: [
            {
                "research_id": 1,
                "question": "Explain RAG",
                "report_excerpt": "RAG retrieves documents.",
                "similarity": 0.9,
            }
        ],
    )

    result = module.retrieve_memory_agent({
        "question": "How does retrieval work?"
    })

    assert len(result["previous_memories"]) == 1


def test_save_memory(monkeypatch):
    monkeypatch.setattr(
        module,
        "save_research",
        lambda **kwargs: 42,
    )

    monkeypatch.setattr(
        module,
        "add_research_to_memory",
        lambda research_id: {
            "status": "indexed",
            "research_id": research_id,
        },
    )

    result = module.save_memory_agent({
        "question": "What is RAG?",
        "report": "RAG uses external knowledge.",
        "hybrid_result": {
            "plan": "Study RAG",
            "analysis": "RAG combines retrieval and generation.",
            "evidence": [],
            "citation_validation": {},
        },
    })

    assert result["research_id"] == 42
    assert result["memory_index_result"]["status"] == "indexed"


def test_knowledge_graph_agent(monkeypatch):
    extraction = {
        "entities": [
            {"name": "RAG", "type": "TECHNIQUE"}
        ],
        "relationships": [],
    }

    monkeypatch.setattr(
        module,
        "extract_entities_and_relationships",
        lambda text, max_characters: extraction,
    )

    saved = []

    monkeypatch.setattr(
        module,
        "save_extraction",
        lambda result, research_id: saved.append(research_id),
    )

    result = module.knowledge_graph_agent({
        "report": "RAG is a technique.",
        "research_id": 42,
    })

    assert len(result["knowledge_extraction"]["entities"]) == 1
    assert saved == [42]


def test_empty_report():
    result = module.save_memory_agent({
        "question": "Empty test",
        "report": "",
        "hybrid_result": {},
    })

    assert "errors" in result