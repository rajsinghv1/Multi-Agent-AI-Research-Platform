
import importlib
import os
from typing import Any


class ResearchIntegrationError(Exception):
    pass


def _get_graph():
    """
    Configure an existing compiled LangGraph graph using:

    RESEARCH_GRAPH_MODULE
    RESEARCH_GRAPH_ATTRIBUTE

    Example:
    RESEARCH_GRAPH_MODULE=app.workflows.memory_graph
    RESEARCH_GRAPH_ATTRIBUTE=graph
    """

    module_name = os.getenv(
        "RESEARCH_GRAPH_MODULE",
        "app.workflows.memory_graph",
    )

    attribute_name = os.getenv(
        "RESEARCH_GRAPH_ATTRIBUTE",
        "graph",
    )

    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise ResearchIntegrationError(
            f"Cannot import workflow module: {module_name}"
        ) from exc

    graph = getattr(module, attribute_name, None)

    if graph is None:
        raise ResearchIntegrationError(
            f"'{attribute_name}' not found in {module_name}. "
            "Check the compiled graph variable name."
        )

    if not callable(getattr(graph, "invoke", None)):
        raise ResearchIntegrationError(
            "Configured object is not a compiled graph "
            "with an invoke() method."
        )

    return graph


def _extract_report(result: Any) -> str:
    if isinstance(result, str):
        return result.strip()

    if not isinstance(result, dict):
        raise ResearchIntegrationError(
            "Workflow returned an unsupported result type."
        )

    for key in (
        "report",
        "final_report",
        "research_report",
        "answer",
        "final_answer",
    ):
        value = result.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    raise ResearchIntegrationError(
        "Workflow finished, but no report field was found. "
        f"Available fields: {list(result.keys())}"
    )


def generate_research(topic: str, depth: str = "detailed"):
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    valid_depths = {
        "brief",
        "detailed",
        "comprehensive",
    }

    if depth not in valid_depths:
        raise ValueError("Invalid research depth.")

    graph = _get_graph()

    state = {
        "topic": topic.strip(),
        "query": topic.strip(),
        "question": topic.strip(),
        "research_depth": depth,
    }

    try:
        result = graph.invoke(state)
    except Exception as exc:
        message = str(exc).lower()

        if any(
            term in message
            for term in (
                "429",
                "resource_exhausted",
                "quota",
                "rate limit",
            )
        ):
            raise ResearchIntegrationError(
                "Gemini API quota or rate limit reached. "
                "Try again after quota availability resets."
            ) from exc

        raise ResearchIntegrationError(
            f"Research workflow failed: {exc}"
        ) from exc

    report = _extract_report(result)

    return {
        "topic": topic.strip(),
        "depth": depth,
        "report": report,
        "raw_result": result,
    }
