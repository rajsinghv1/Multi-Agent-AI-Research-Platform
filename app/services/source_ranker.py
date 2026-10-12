import re
from urllib.parse import urlsplit, urlunsplit

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize(text):
    return re.sub(
        r"\s+", " ",
        re.sub(r"[^\w\s]", " ", str(text).lower())
    ).strip()


def source_identity(source):
    doi = str(source.get("doi") or "").strip().lower()

    if doi:
        return "doi:" + doi.removeprefix("https://doi.org/")

    url = str(source.get("url") or "").strip()
    if url:
        parsed = urlsplit(url)
        return "url:" + urlunsplit((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            "", ""
        ))

    return "title:" + normalize(source.get("title", ""))


def deduplicate_sources(sources):
    unique = []
    seen_ids = set()
    seen_titles = set()

    for source in sources:
        identity = source_identity(source)
        title = normalize(source.get("title", ""))

        if identity in seen_ids:
            continue

        if title and title in seen_titles:
            continue

        seen_ids.add(identity)

        if title:
            seen_titles.add(title)

        unique.append(source.copy())

    return unique


def rank_sources(query, sources, threshold=0.08):
    if not sources:
        return []

    documents = [
        (
            str(s.get("title") or "") + " "
            + str(s.get("title") or "") + " "
            + str(s.get("summary") or "")[:1500]
        )
        for s in sources
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    matrix = vectorizer.fit_transform([query] + documents)

    scores = cosine_similarity(
        matrix[0:1], matrix[1:]
    )[0]

    ranked = []

    for source, score in zip(sources, scores):
        score = float(score)

        if score >= threshold:
            item = source.copy()
            item["relevance_score"] = round(score, 4)
            ranked.append(item)

    return sorted(
        ranked,
        key=lambda item: item["relevance_score"],
        reverse=True
    )


def filter_and_rank(query, sources, threshold=0.08):
    unique = deduplicate_sources(sources)
    return rank_sources(query, unique, threshold)