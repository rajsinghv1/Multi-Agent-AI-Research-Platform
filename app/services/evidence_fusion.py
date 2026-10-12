def fuse_evidence(web_sources, document_sources):
    evidence = []
    seen_web = set()
    seen_documents = set()

    for source in web_sources:
        title = source.get("title", "Untitled")
        url = source.get("url", "")

        key = (url or title).strip().lower()

        if key in seen_web:
            continue

        seen_web.add(key)

        citation = f"S{len(seen_web)}"

        evidence.append({
            "citation": citation,
            "type": "web",
            "title": title,
            "url": url,
            "provider": source.get("source", "unknown"),
            "text": (
                source.get("summary")
                or source.get("abstract")
                or source.get("text")
                or ""
            ),
            "score": source.get(
                "relevance_score",
                source.get("score")
            ),
        })

    for source in document_sources:
        fingerprint = source.get(
            "document_hash",
            source.get("source", "")
        )

        key = (
            fingerprint,
            source.get("page"),
            source.get("text", "")
        )

        if key in seen_documents:
            continue

        seen_documents.add(key)

        citation = f"D{len(seen_documents)}"

        evidence.append({
            "citation": citation,
            "type": "document",
            "title": source.get("source", "Unknown PDF"),
            "page": source.get("page"),
            "text": source.get("text", ""),
            "score": source.get("score"),
        })

    return evidence


def format_evidence(evidence):
    blocks = []

    for item in evidence:
        citation = item["citation"]

        if item["type"] == "web":
            location = (
                f"URL: {item['url']}\n"
                f"Provider: {item['provider']}"
            )
        else:
            location = (
                f"PDF: {item['title']}\n"
                f"Page: {item['page']}"
            )

        blocks.append(
            f"[{citation}]\n"
            f"{location}\n"
            f"Content:\n{item['text']}"
        )

    return "\n\n".join(blocks)