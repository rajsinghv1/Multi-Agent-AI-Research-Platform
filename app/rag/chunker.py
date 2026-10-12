def chunk_documents(
    pages,
    chunk_size=1000,
    overlap=200
):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if not 0 <= overlap < chunk_size:
        raise ValueError(
            "overlap must be between 0 and chunk_size"
        )

    chunks = []

    for page in pages:
        text = page["text"]
        step = chunk_size - overlap

        for start in range(0, len(text), step):
            chunk_text = text[start:start + chunk_size]

            if not chunk_text.strip():
                continue

            chunks.append({
                "id": len(chunks),
                "source": page["source"],
                "page": page["page"],
                "text": chunk_text
            })

            if start + chunk_size >= len(text):
                break

    return chunks