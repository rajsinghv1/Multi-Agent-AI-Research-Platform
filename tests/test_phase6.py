import numpy as np
import pytest

from app.services.evidence_fusion import (
    fuse_evidence,
    format_evidence,
)
from app.services.hybrid_citations import (
    validate_hybrid_citations,
)
from app.rag import multi_document_store as store
from app.workflows.hybrid_graph import hybrid_graph


def sample_evidence():
    web = [
        {
            "title": "RAG Research",
            "url": "https://example.org/paper",
            "source": "arxiv",
            "summary": "RAG combines retrieval and generation.",
        },
        {
            "title": "Duplicate RAG Research",
            "url": "https://example.org/paper",
            "source": "arxiv",
            "summary": "Duplicate",
        },
    ]

    documents = [
        {
            "source": "research.pdf",
            "page": 2,
            "text": "RAG uses a retriever and generator.",
            "document_hash": "abc123",
            "score": 0.85,
        }
    ]

    return fuse_evidence(web, documents)


def test_evidence_fusion():
    evidence = sample_evidence()

    assert len(evidence) == 2
    assert evidence[0]["citation"] == "S1"
    assert evidence[1]["citation"] == "D1"


def test_evidence_formatting():
    context = format_evidence(sample_evidence())

    assert "[S1]" in context
    assert "[D1]" in context
    assert "Page: 2" in context


def test_valid_citations():
    result = validate_hybrid_citations(
        "Research uses retrieval [S1] "
        "and a generator [D1].",
        sample_evidence(),
    )

    assert result["passed"] is True
    assert result["citation_coverage"] == 1.0


def test_invalid_citations():
    result = validate_hybrid_citations(
        "Unsupported claim [D99].",
        sample_evidence(),
    )

    assert result["passed"] is False
    assert result["invalid_citations"] == ["D99"]


def test_graph_structure():
    graph = hybrid_graph.get_graph()

    nodes = set(graph.nodes.keys())

    assert {
        "planning",
        "research",
        "evidence_fusion",
        "analysis",
        "report",
    }.issubset(nodes)


def test_multi_document_store(tmp_path, monkeypatch):
    monkeypatch.setattr(
        store,
        "STORE_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        store,
        "INDEX_PATH",
        tmp_path / "documents.index"
    )
    monkeypatch.setattr(
        store,
        "META_PATH",
        tmp_path / "documents.json"
    )

    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"synthetic PDF placeholder")

    monkeypatch.setattr(
        store,
        "load_pdf",
        lambda path: [{
            "source": "test.pdf",
            "page": 1,
            "text": "Retrieval augmented generation",
        }]
    )

    monkeypatch.setattr(
        store,
        "embed_documents",
        lambda texts: np.array(
            [[1.0, 0.0, 0.0]],
            dtype=np.float32
        )
    )

    monkeypatch.setattr(
        store,
        "embed_query",
        lambda question: np.array(
            [[1.0, 0.0, 0.0]],
            dtype=np.float32
        )
    )

    first = store.index_document(pdf)
    second = store.index_document(pdf)

    assert first["status"] == "indexed"
    assert second["status"] == "already_indexed"

    results = store.search_documents(
        "What is RAG?"
    )

    assert len(results) == 1
    assert results[0]["source"] == "test.pdf"
    assert results[0]["score"] > 0.99