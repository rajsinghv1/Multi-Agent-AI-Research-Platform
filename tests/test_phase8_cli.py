
import json
import pytest

from app.phase8_cli import (
    build_markdown,
    export_evaluation,
)


def test_build_markdown():
    from app.evaluation.unified_evaluator import evaluate_research

    result = evaluate_research(
        "# Introduction\nRAG improves accuracy [D1]."
    )

    markdown = build_markdown(1, result)

    assert "# Research Evaluation Report" in markdown
    assert "Research ID: 1" in markdown
    assert "## Quality" in markdown


def test_export_evaluation(tmp_path, monkeypatch):
    import app.phase8_cli as cli

    monkeypatch.setattr(
        cli,
        "get_research",
        lambda research_id: {
            "report": (
                "# Introduction\n"
                "RAG improves factual accuracy [D1]."
            )
        },
    )

    json_path, md_path = export_evaluation(
        1,
        output_dir=tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()

    data = json.loads(
        json_path.read_text(encoding="utf-8")
    )

    assert "quality" in data
    assert "research_gaps" in data


def test_missing_research(tmp_path, monkeypatch):
    import app.phase8_cli as cli

    monkeypatch.setattr(
        cli,
        "get_research",
        lambda research_id: None,
    )

    with pytest.raises(ValueError):
        export_evaluation(
            999,
            output_dir=tmp_path,
        )
