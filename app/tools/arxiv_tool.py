import arxiv


def search_arxiv(query: str, max_results: int = 5):
    papers = []

    client = arxiv.Client(
        page_size=max_results,
        delay_seconds=3,
        num_retries=2
    )

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    for paper in client.results(search):
        papers.append({
            "source": "arxiv",
            "title": paper.title,
            "authors": [
                author.name for author in paper.authors
            ],
            "summary": paper.summary,
            "published": paper.published.isoformat(),
            "url": paper.entry_id,
            "pdf_url": paper.pdf_url
        })

    return papers