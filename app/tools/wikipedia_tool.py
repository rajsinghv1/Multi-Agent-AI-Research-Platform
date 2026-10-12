import requests


API_URL = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": (
        "MultiAgentResearchPlatform/0.1 "
        "(educational research project)"
    )
}


def search_wikipedia(query: str, limit: int = 3):
    response = requests.get(
        API_URL,
        params={
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": limit,
            "prop": "extracts|info",
            "exintro": 1,
            "explaintext": 1,
            "inprop": "url",
            "format": "json",
            "formatversion": 2
        },
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    pages = response.json().get(
        "query", {}
    ).get("pages", [])

    results = []

    for page in pages:
        results.append({
            "source": "wikipedia",
            "title": page.get("title", ""),
            "summary": page.get("extract", "")[:3000],
            "url": page.get("fullurl", ""),
            "published": None,
            "authors": []
        })

    return results