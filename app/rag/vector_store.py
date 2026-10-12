import json
from pathlib import Path

import faiss
import numpy as np


STORE_DIR = Path("data/vectorstore")
INDEX_PATH = STORE_DIR / "research.index"
META_PATH = STORE_DIR / "metadata.json"


def create_index(chunks, embeddings):
    if not chunks:
        raise ValueError("No document chunks to index")

    vectors = np.asarray(
        embeddings, dtype=np.float32
    )

    if vectors.ndim != 2 or len(vectors) != len(chunks):
        raise ValueError(
            "Embedding matrix and chunks do not match"
        )

    vectors = np.ascontiguousarray(vectors)
    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    STORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    META_PATH.write_text(
        json.dumps(
            chunks,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    return index


def search_index(query_vector, top_k=5):
    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            "FAISS index missing. Index a PDF first."
        )

    if not META_PATH.exists():
        raise FileNotFoundError(
            "Vector metadata file missing."
        )

    index = faiss.read_index(str(INDEX_PATH))

    metadata = json.loads(
        META_PATH.read_text(encoding="utf-8")
    )

    if len(metadata) != index.ntotal:
        raise ValueError(
            "Index and metadata are inconsistent"
        )

    query = np.asarray(
        query_vector,
        dtype=np.float32
    ).reshape(1, -1)

    if query.shape[1] != index.d:
        raise ValueError(
            "Query embedding dimension mismatch"
        )

    faiss.normalize_L2(query)

    scores, indices = index.search(
        query,
        min(top_k, index.ntotal)
    )

    results = []

    for score, idx in zip(
        scores[0],
        indices[0]
    ):
        if idx < 0:
            continue

        item = metadata[int(idx)].copy()
        item["score"] = float(score)
        results.append(item)

    return results