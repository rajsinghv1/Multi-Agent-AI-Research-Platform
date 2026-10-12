import hashlib
import json
from pathlib import Path

import faiss
import numpy as np

from app.rag.pdf_loader import load_pdf
from app.rag.chunker import chunk_documents
from app.rag.embeddings import (
    embed_documents,
    embed_query,
)


STORE_DIR = Path("data/vectorstore/multi")
INDEX_PATH = STORE_DIR / "documents.index"
META_PATH = STORE_DIR / "documents.json"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_store():
    if not INDEX_PATH.exists() and not META_PATH.exists():
        return None, []

    if not INDEX_PATH.exists() or not META_PATH.exists():
        raise RuntimeError(
            "Incomplete vector store: index or metadata missing"
        )

    index = faiss.read_index(str(INDEX_PATH))

    metadata = json.loads(
        META_PATH.read_text(encoding="utf-8")
    )

    if index.ntotal != len(metadata):
        raise RuntimeError(
            "FAISS index and metadata are inconsistent"
        )

    return index, metadata


def save_store(index, metadata):
    STORE_DIR.mkdir(parents=True, exist_ok=True)

    # Write temporary files before replacing active files.
    temporary_index = STORE_DIR / "documents.index.tmp"
    temporary_meta = STORE_DIR / "documents.json.tmp"

    faiss.write_index(index, str(temporary_index))

    temporary_meta.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # This protects each individual file replacement.
    # It is not a fully transactional two-file commit.
    temporary_index.replace(INDEX_PATH)
    temporary_meta.replace(META_PATH)


def document_hash(pdf_path):
    digest = hashlib.sha256()

    with open(pdf_path, "rb") as file:
        for block in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(block)

    return digest.hexdigest()


def index_document(pdf_path):
    pdf_path = Path(pdf_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)

    fingerprint = document_hash(pdf_path)

    index, metadata = load_store()

    if any(
        item["document_hash"] == fingerprint
        for item in metadata
    ):
        return {
            "status": "already_indexed",
            "file": pdf_path.name,
            "chunks_added": 0,
            "total_chunks": len(metadata),
        }

    pages = load_pdf(pdf_path)

    if not pages:
        raise ValueError(
            "No extractable PDF text found"
        )

    chunks = chunk_documents(
        pages,
        chunk_size=CHUNK_SIZE,
        overlap=CHUNK_OVERLAP
    )

    for chunk in chunks:
        chunk["document_hash"] = fingerprint

    vectors = np.asarray(
        embed_documents(
            [chunk["text"] for chunk in chunks]
        ),
        dtype=np.float32
    )

    if vectors.ndim != 2 or len(vectors) != len(chunks):
        raise RuntimeError(
            "Embedding output shape is invalid"
        )

    vectors = np.ascontiguousarray(vectors)
    faiss.normalize_L2(vectors)

    if index is None:
        index = faiss.IndexFlatIP(vectors.shape[1])

    if index.d != vectors.shape[1]:
        raise ValueError(
            "Embedding dimension mismatch"
        )

    index.add(vectors)

    metadata.extend(chunks)

    save_store(index, metadata)

    return {
        "status": "indexed",
        "file": pdf_path.name,
        "chunks_added": len(chunks),
        "total_chunks": len(metadata),
    }


def search_documents(question, top_k=5):
    if top_k < 1:
        raise ValueError("top_k must be positive")

    index, metadata = load_store()

    if index is None or index.ntotal == 0:
        return []

    query_vector = np.asarray(
        embed_query(question),
        dtype=np.float32
    ).reshape(1, -1)

    if query_vector.shape[1] != index.d:
        raise ValueError(
            "Query embedding dimension mismatch"
        )

    faiss.normalize_L2(query_vector)

    scores, positions = index.search(
        query_vector,
        min(top_k, index.ntotal)
    )

    results = []

    for score, position in zip(
        scores[0],
        positions[0]
    ):
        if position < 0:
            continue

        item = metadata[int(position)].copy()
        item["score"] = float(score)

        results.append(item)

    return results