import json
import pytest

from app.services import entity_extractor


def test_valid_json():
    response = json.dumps({
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
    })

    result = entity_extractor.parse_extraction_json(response)

    assert len(result["entities"]) == 2
    assert len(result["relationships"]) == 1


def test_markdown_json():
    response = """```json
{
  "entities": [{"name": "Gemini", "type": "MODEL"}],
  "relationships": []
}
```"""

    result = entity_extractor.parse_extraction_json(response)

    assert result["entities"][0]["name"] == "Gemini"


def test_duplicate_entities():
    response = json.dumps({
        "entities": [
            {"name": "FAISS", "type": "TOOL"},
            {"name": "faiss", "type": "TOOL"},
        ],
        "relationships": [],
    })

    result = entity_extractor.parse_extraction_json(response)

    assert len(result["entities"]) == 1


def test_invalid_relationship():
    response = json.dumps({
        "entities": [
            {"name": "RAG", "type": "TECHNIQUE"},
        ],
        "relationships": [
            {
                "source": "RAG",
                "relation": "USES",
                "target": "Unknown Tool",
            }
        ],
    })

    result = entity_extractor.parse_extraction_json(response)

    assert result["relationships"] == []


def test_invalid_json():
    with pytest.raises(ValueError):
        entity_extractor.parse_extraction_json(
            "not valid JSON"
        )


def test_mock_gemini(monkeypatch):
    mock_response = json.dumps({
        "entities": [
            {"name": "LangGraph", "type": "FRAMEWORK"},
        ],
        "relationships": [],
    })

    monkeypatch.setattr(
        entity_extractor,
        "generate_response",
        lambda prompt: mock_response,
    )

    result = entity_extractor.extract_entities_and_relationships(
        "LangGraph orchestrates research agents."
    )

    assert result["entities"][0]["name"] == "LangGraph"


def test_empty_text():
    with pytest.raises(ValueError):
        entity_extractor.extract_entities_and_relationships("")