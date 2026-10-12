import re


def validate_citations(report, sources):
    cited_ids = {
        int(value)
        for value in re.findall(
            r"\[S(\d+)\]", report
        )
    }

    valid_ids = set(
        range(1, len(sources) + 1)
    )

    invalid = sorted(cited_ids - valid_ids)
    valid = sorted(cited_ids & valid_ids)

    return {
        "valid_citations": valid,
        "invalid_citations": invalid,
        "citation_count": len(cited_ids),
        "source_count": len(sources),
        "citation_coverage": round(
            len(valid) / len(sources), 3
        ) if sources else 0.0,
        "passed": len(invalid) == 0
    }