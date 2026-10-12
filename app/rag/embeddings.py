import numpy as np
from google import genai
from google.genai import types

from app.core.config import settings


EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768


client = genai.Client(
    api_key=settings.GOOGLE_API_KEY
)


def embed_texts(texts, task_type):
    if not texts:
        return np.empty(
            (0, EMBEDDING_DIM),
            dtype=np.float32
        )

    vectors = []

    # Small batches reduce request size.
    # Free-tier rate limits still apply.
    for start in range(0, len(texts), 10):
        batch = texts[start:start + 10]

        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBEDDING_DIM
            )
        )

        if len(response.embeddings) != len(batch):
            raise RuntimeError(
                "Embedding count does not match input count"
            )

        for embedding in response.embeddings:
            vectors.append(embedding.values)

    return np.asarray(vectors, dtype=np.float32)


def embed_documents(texts):
    return embed_texts(
        texts,
        "RETRIEVAL_DOCUMENT"
    )


def embed_query(query):
    return embed_texts(
        [query],
        "RETRIEVAL_QUERY"
    )