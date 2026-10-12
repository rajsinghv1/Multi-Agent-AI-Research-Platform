from concurrent.futures import ThreadPoolExecutor

from app.tools.arxiv_tool import search_arxiv
from app.tools.wikipedia_tool import search_wikipedia
from app.tools.crossref_tool import search_crossref

from app.services.source_ranker import filter_and_rank
from app.services.research_cache import (
    get_cached,
    save_cache
)
from app.services.quality_metrics import (
    calculate_quality_metrics
)


def collect_research(query: str):
    cached = get_cached(query)

    if cached is not None:
        print("[CACHE HIT] Using cached research")
        return cached

    print("[CACHE MISS] Searching research APIs")

    tools = {
        "arxiv": search_arxiv,
        "wikipedia": search_wikipedia,
        "crossref": search_crossref
    }

    sources = []
    errors = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            name: executor.submit(func, query)
            for name, func in tools.items()
        }

        for name, future in futures.items():
            try:
                results = future.result(timeout=90)
                sources.extend(results)

                print(
                    f"[OK] {name}: "
                    f"{len(results)} results"
                )

            except Exception as error:
                errors.append({
                    "source": name,
                    "error": str(error)
                })
                print(f"[ERROR] {name}: {error}")

    ranked = filter_and_rank(
        query=query,
        sources=sources,
        threshold=0.08
    )

    metrics = calculate_quality_metrics(
        raw_sources=sources,
        ranked_sources=ranked,
        errors=errors
    )

    result = {
        "query": query,
        "sources": ranked,
        "total_sources": len(ranked),
        "errors": errors,
        "metrics": metrics
    }

    # Cache only fully successful retrievals.
    # Partial failures should be retried next time.
    if not errors and ranked:
        save_cache(query, result)

    print("\nRESEARCH QUALITY METRICS")

    for key, value in metrics.items():
        print(f"{key}: {value}")

    return result