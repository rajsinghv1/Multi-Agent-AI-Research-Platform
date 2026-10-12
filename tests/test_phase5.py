import numpy as np

from app.rag.chunker import chunk_documents
import app.rag.vector_store as store


def test_document_chunking():
    pages = [{
        "source": "test.pdf",
        "page": 1,
        "text": "A" * 2500
    }]

    chunks = chunk_documents(
        pages,
        chunk_size=1000,
        overlap=200
    )

    assert len(chunks) == 3
    assert chunks[0]["page"] == 1
    assert chunks[0]["source"] == "test.pdf"


def test_chunk_overlap():
    pages = [{
        "source": "test.pdf",
        "page": 2,
        "text": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    }]

    chunks = chunk_documents(
        pages,
        chunk_size=10,
        overlap=3
    )

    assert chunks[0]["text"][-3:] == (
        chunks[1]["text"][:3]
    )


def test_vector_store(tmp_path, monkeypatch):
    monkeypatch.setattr(
        store,
        "STORE_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        store,
        "INDEX_PATH",
        tmp_path / "research.index"
    )
    monkeypatch.setattr(
        store,
        "META_PATH",
        tmp_path / "metadata.json"
    )

    chunks = [
        {
            "id": 0,
            "source": "test.pdf",
            "page": 1,
            "text": "Retrieval augmented generation"
        },
        {
            "id": 1,
            "source": "test.pdf",
            "page": 2,
            "text": "Machine learning algorithms"
        }
    ]

    embeddings = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ], dtype=np.float32)

    store.create_index(
        chunks,
        embeddings
    )

    query = np.array(
        [1.0, 0.0, 0.0],
        dtype=np.float32
    )

    results = store.search_index(
        query,
        top_k=1
    )

    assert len(results) == 1
    assert results[0]["page"] == 1
    assert results[0]["score"] > 0.99