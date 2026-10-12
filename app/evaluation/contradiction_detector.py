
import re
from difflib import SequenceMatcher

NEGATIONS = {
    "not", "no", "never", "cannot", "without",
    "neither", "nor", "doesn't", "don't",
    "isn't", "aren't", "wasn't", "weren't",
    "won't", "can't", "didn't",
}

STOPWORDS = {
    "the", "a", "an", "is", "are", "was",
    "were", "to", "of", "in", "on", "for",
    "with", "and", "or", "that", "this",
    "it", "by", "from", "as", "be", "can",
    "does", "do", "did", "will", "would",
    "should", "has", "have", "had",
}

CONTRACTIONS = {
    "doesn't": "does not",
    "don't": "do not",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "won't": "will not",
    "can't": "cannot",
    "didn't": "did not",
}


def normalize_text(text):
    if not isinstance(text, str):
        raise TypeError("Claim must be a string.")

    text = text.lower().strip()

    for short, expanded in CONTRACTIONS.items():
        text = text.replace(short, expanded)

    text = re.sub(r"\[[A-Za-z]+\d+\]", "", text)
    text = re.sub(r"[^\w\s]", " ", text)

    return " ".join(text.split())


def tokenize(text):
    return normalize_text(text).split()


def has_negation(text):
    return any(
        token in NEGATIONS
        for token in tokenize(text)
    )


def content_tokens(text):
    return {
        token
        for token in tokenize(text)
        if token not in STOPWORDS
        and token not in NEGATIONS
    }


def calculate_similarity(claim_a, claim_b):
    tokens_a = content_tokens(claim_a)
    tokens_b = content_tokens(claim_b)

    if not tokens_a or not tokens_b:
        return 0.0

    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)

    jaccard = intersection / union

    text_a = " ".join(sorted(tokens_a))
    text_b = " ".join(sorted(tokens_b))

    sequence_score = SequenceMatcher(
        None, text_a, text_b
    ).ratio()

    return round(
        0.7 * jaccard + 0.3 * sequence_score,
        4
    )


def detect_contradiction(
    claim_a,
    claim_b,
    similarity_threshold=0.65,
):
    """
    Detect potential negation-based contradictions.

    This is a heuristic, not an NLI model.
    """

    similarity = calculate_similarity(
        claim_a, claim_b
    )

    negation_a = has_negation(claim_a)
    negation_b = has_negation(claim_b)

    opposite_polarity = negation_a != negation_b

    is_contradiction = (
        similarity >= similarity_threshold
        and opposite_polarity
    )

    confidence = (
        round(similarity * 100, 2)
        if is_contradiction
        else 0.0
    )

    return {
        "claim_a": claim_a,
        "claim_b": claim_b,
        "similarity": similarity,
        "opposite_polarity": opposite_polarity,
        "is_contradiction": is_contradiction,
        "confidence": confidence,
        "method": "lexical_negation_heuristic",
    }


def analyze_evidence(
    evidence,
    similarity_threshold=0.65,
):
    """
    evidence example:
    [
        {
            "source": "D1",
            "claim": "RAG improves accuracy."
        },
        {
            "source": "D2",
            "claim": "RAG does not improve accuracy."
        }
    ]
    """

    if not isinstance(evidence, list):
        raise TypeError("Evidence must be a list.")

    contradictions = []
    checked_pairs = 0

    for i in range(len(evidence)):
        for j in range(i + 1, len(evidence)):

            first = evidence[i]
            second = evidence[j]

            if not isinstance(first, dict) or not isinstance(second, dict):
                raise TypeError("Each evidence item must be a dictionary.")

            claim_a = first.get("claim", "")
            claim_b = second.get("claim", "")

            if not isinstance(claim_a, str) or not isinstance(claim_b, str):
                raise TypeError("Evidence claims must be strings.")

            if not claim_a.strip() or not claim_b.strip():
                continue

            checked_pairs += 1

            result = detect_contradiction(
                claim_a,
                claim_b,
                similarity_threshold,
            )

            if result["is_contradiction"]:
                contradictions.append({
                    "source_a": first.get("source", "unknown"),
                    "source_b": second.get("source", "unknown"),
                    **result,
                })

    return {
        "total_evidence": len(evidence),
        "checked_pairs": checked_pairs,
        "contradictions_found": len(contradictions),
        "contradictions": contradictions,
    }
