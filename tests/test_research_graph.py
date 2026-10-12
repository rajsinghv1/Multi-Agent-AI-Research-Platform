from app.workflows.research_graph import build_research_graph


def test_graph_structure():
    graph = build_research_graph()
    nodes = graph.get_graph().nodes

    expected = [
        "planning_agent",
        "research_agent",
        "analysis_agent",
        "report_agent",
    ]

    for node in expected:
        assert node in nodes


if __name__ == "__main__":
    test_graph_structure()
    print("Phase 2 graph structure test PASSED")