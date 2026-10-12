import json
import os
import tempfile
from pathlib import Path

import faiss
import numpy as np

from app.memory.database import get_research
from app.rag.embeddings import embed_documents, embed_query


MEMORY_DIR = Path("data/memory/semantic")
INDEX_PATH = MEMORY_DIR / "memory.index"
META_PATH = MEMORY_DIR / "memory.json"


def _normalize(vector):
    arr = np.asarray(vector, dtype=np.float32)

    if arr.ndim == 1:
        arr = arr.reshape(1, -1)

    if arr.ndim != 2 or arr.shape[1] == 0:
        raise ValueError("Invalid embedding dimensions")

    if not np.all(np.isfinite(arr)):
        raise ValueError("Embedding contains invalid values")

    faiss.normalize_L2(arr)
    return arr


def _load_store():
    if not INDEX_PATH.exists() and not META_PATH.exists():
        return None, []

    if not INDEX_PATH.exists() or not META_PATH.exists():
        raise RuntimeError("Semantic memory files are incomplete")

    index = faiss.read_index(str(INDEX_PATH))

    with META_PATH.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    if not isinstance(metadata, list):
        raise ValueError("Invalid memory metadata")

    if index.ntotal != len(metadata):
        raise RuntimeError("FAISS and metadata counts do not match")

    return index, metadata


def _save_store(index, metadata):
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    # Write temporary files before replacing the existing files.
    with tempfile.NamedTemporaryFile(
        dir=MEMORY_DIR,
        suffix=".index",
        delete=False,
    ) as tmp:
        temporary_index = Path(tmp.name)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=MEMORY_DIR,
        suffix=".json",
        delete=False,
    ) as tmp:
        temporary_meta = Path(tmp.name)

    try:
        faiss.write_index(index, str(temporary_index))

        with temporary_meta.open("w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=2)

        os.replace(temporary_index, INDEX_PATH)
        os.replace(temporary_meta, META_PATH)

    finally:
        temporary_index.unlink(missing_ok=True)
        temporary_meta.unlink(missing_ok=True)


def add_research_to_memory(research_id):
    """
    Embed a saved research record and add it to FAISS.
    """

    research = get_research(research_id)

    if research is None:
        raise ValueError(f"Research ID {research_id} not found")

    index, metadata = _load_store()

    if any(item["research_id"] == research_id for item in metadata):
        return {
            "status": "already_indexed",
            "research_id": research_id,
        }

    text = (
        f"Question: {research['question']}\n"
        f"Research report:\n{research['report'][:12000]}"
    )

    embeddings = embed_documents([text])
    vectors = _normalize(embeddings)

    if vectors.shape[0] != 1:
        raise ValueError("Expected one research embedding")

    if index is None:
        index = faiss.IndexFlatIP(vectors.shape[1])
    elif index.d != vectors.shape[1]:
        raise ValueError("Embedding dimension mismatch")

    index.add(vectors)

    metadata.append({
        "research_id": research_id,
        "question": research["question"],
        "created_at": research["created_at"],
    })

    _save_store(index, metadata)

    return {
        "status": "indexed",
        "research_id": research_id,
        "total_memories": index.ntotal,
    }


def search_memory(question, top_k=5, min_score=0.0):
    """
    Search previous research using cosine similarity.
    """

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Search question cannot be empty")

    index, metadata = _load_store()

    if index is None or index.ntotal == 0:
        return []

    query_vector = _normalize(embed_query(question))

    if query_vector.shape[1] != index.d:
        raise ValueError("Query embedding dimension mismatch")

    k = min(max(1, int(top_k)), index.ntotal)

    scores, indices = index.search(query_vector, k)

    results = []

    for score, position in zip(scores[0], indices[0]):
        if position < 0 or float(score) < min_score:
            continue

        item = metadata[int(position)]
        research = get_research(item["research_id"])

        # Ignore records deleted from SQLite.
        if research is None:
            continue

        results.append({
            "research_id": research["id"],
            "question": research["question"],
            "report_excerpt": research["report"][:1000],
            "similarity": round(float(score), 4),
        })

    return results


def get_memory_stats():
    index, metadata = _load_store()

    return {
        "total_memories": len(metadata),
        "embedding_dimensions": index.d if index else 0,
    }