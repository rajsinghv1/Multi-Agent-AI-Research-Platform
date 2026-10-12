import re


CITATION_PATTERN = re.compile(r"\[([SD]\d+)\]")


def validate_hybrid_citations(report, evidence):
    valid_ids = {
        item["citation"]
        for item in evidence
    }

    used_ids = set(
        CITATION_PATTERN.findall(report)
    )

    invalid = sorted(used_ids - valid_ids)
    valid = sorted(used_ids & valid_ids)

    coverage = (
        len(valid) / len(valid_ids)
        if valid_ids else 0.0
    )

    return {
        "valid_citations": valid,
        "invalid_citations": invalid,
        "citation_count": len(used_ids),
        "evidence_count": len(valid_ids),
        "citation_coverage": round(coverage, 4),
        "passed": (
            bool(valid_ids)
            and bool(valid)
            and not invalid
        ),
    }