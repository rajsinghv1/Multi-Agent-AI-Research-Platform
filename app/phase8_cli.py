
import argparse
import json
from pathlib import Path

from app.memory.database import get_research
from app.evaluation.unified_evaluator import evaluate_research


def build_markdown(research_id, result):
    quality = result["quality"]
    gaps = result["research_gaps"]
    contradictions = result["contradictions"]
    credibility = result["credibility"]

    lines = [
        "# Research Evaluation Report",
        "",
        f"Research ID: {research_id}",
        "",
        "## Quality",
        f"- Score: {quality['overall_score']}/100",
        f"- Grade: {quality['grade']}",
        "",
        "## Research Gaps",
        f"- Gap matches: {gaps['total_explicit_gaps']}",
        f"- Missing sections: {', '.join(gaps['missing_sections']) or 'None'}",
        "",
        "## Contradictions",
        f"- Potential contradictions: {contradictions['contradictions_found']}",
        f"- Evidence pairs checked: {contradictions['checked_pairs']}",
        "",
        "## Source Credibility",
        f"- Sources evaluated: {credibility['total_sources']}",
        f"- Average heuristic score: {credibility['average_score']}",
        "",
        "## Warnings",
    ]

    lines.extend(
        f"- {warning}"
        for warning in result["warnings"]
    )

    if not result["warnings"]:
        lines.append("- None")

    return "\n".join(lines) + "\n"


def export_evaluation(research_id, output_dir="outputs/evaluations"):
    research = get_research(research_id)

    if not research:
        raise ValueError(
            f"Research ID {research_id} not found."
        )

    result = evaluate_research(research["report"])

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    json_path = directory / f"research_{research_id}_evaluation.json"
    markdown_path = directory / f"research_{research_id}_evaluation.md"

    json_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    markdown_path.write_text(
        build_markdown(research_id, result),
        encoding="utf-8",
    )

    return json_path, markdown_path


def main():
    parser = argparse.ArgumentParser(
        description="Offline Research Evaluation CLI"
    )

    parser.add_argument(
        "--research-id",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        default="outputs/evaluations",
    )

    args = parser.parse_args()

    try:
        json_path, markdown_path = export_evaluation(
            args.research_id,
            args.output_dir,
        )
    except ValueError as exc:
        parser.exit(1, f"Error: {exc}\n")

    print("[OK] Research evaluation complete")
    print(f"JSON: {json_path}")
    print(f"Markdown: {markdown_path}")


if __name__ == "__main__":
    main()
