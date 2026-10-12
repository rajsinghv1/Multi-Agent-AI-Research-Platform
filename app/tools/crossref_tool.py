import re
import requests


def clean_text(text):
    return re.sub(r"<[^>]+>", " ", text or "").strip()


def search_crossref(query: str, limit: int = 5):
    response = requests.get(
        "https://api.crossref.org/works",
        params={
            "query.bibliographic": query,
            "rows": limit,
            "select": (
                "DOI,title,author,published,"
                "abstract,URL"
            )
        },
        headers={
            "User-Agent": "MultiAgentResearchPlatform/0.1"
        },
        timeout=25
    )

    response.raise_for_status()

    items = response.json()["message"]["items"]
    results = []

    for item in items:
        authors = [
            " ".join(filter(None, [
                author.get("given", ""),
                author.get("family", "")
            ]))
            for author in item.get("author", [])
        ]

        results.append({
            "source": "crossref",
            "title": (
                item.get("title") or [""]
            )[0],
            "authors": authors,
            "summary": clean_text(
                item.get("abstract", "")
            ),
            "published": item.get("published"),
            "url": item.get("URL", ""),
            "doi": item.get("DOI", "")
        })

    return results