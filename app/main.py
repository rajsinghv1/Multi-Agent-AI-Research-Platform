from app.workflows.research_graph import build_research_graph


def main():
    print("=" * 60)
    print("MULTI-AGENT AI RESEARCH PLATFORM — PHASE 4")
    print("=" * 60)

    # =====================================================
    # USER RESEARCH QUESTION
    # =====================================================

    query = input(
        "\nEnter research question: "
    ).strip()

    if not query:
        print("Research question cannot be empty.")
        return

    # =====================================================
    # BUILD LANGGRAPH WORKFLOW
    # =====================================================

    graph = build_research_graph()

    initial_state = {
        "query": query,
        "plan": "",
        "research": "",
        "analysis": "",
        "report": "",
        "sources": [],
        "errors": [],
        "metrics": {},
        "citation_validation": {}
    }

    print("\nStarting Multi-Agent Research Workflow...")

    result = graph.invoke(initial_state)

    # =====================================================
    # FINAL RESEARCH REPORT
    # =====================================================

    print("\n" + "=" * 60)
    print("FINAL RESEARCH REPORT")
    print("=" * 60)

    print(result.get("report", "No report generated."))

    # =====================================================
    # RETRIEVED SOURCES
    # =====================================================

    print("\n" + "=" * 60)
    print("RETRIEVED RESEARCH SOURCES")
    print("=" * 60)

    sources = result.get("sources", [])

    if sources:
        for index, source in enumerate(sources, 1):

            print(
                f"\n[S{index}] "
                f"{source.get('title', 'Unknown Title')}"
            )

            print(
                f"Source: {source.get('source', 'Unknown')}"
            )

            print(
                f"URL: {source.get('url', 'N/A')}"
            )

            print(
                f"Relevance Score: "
                f"{source.get('relevance_score', 0.0):.4f}"
            )

    else:
        print("No research sources retrieved.")

    print(f"\nTotal Sources: {len(sources)}")

    # =====================================================
    # PHASE 4 RESEARCH QUALITY METRICS
    # =====================================================

    print("\n" + "=" * 60)
    print("PHASE 4 RESEARCH QUALITY METRICS")
    print("=" * 60)

    metrics = result.get("metrics", {})

    if metrics:
        for key, value in metrics.items():
            print(f"{key}: {value}")
    else:
        print("No research quality metrics available.")

    # =====================================================
    # CITATION VALIDATION
    # =====================================================

    print("\n" + "=" * 60)
    print("CITATION VALIDATION")
    print("=" * 60)

    citation_validation = result.get(
        "citation_validation", {}
    )

    if citation_validation:

        for key, value in citation_validation.items():
            print(f"{key}: {value}")

        if citation_validation.get("passed", False):
            print("\n[PASS] Citation IDs are valid.")
        else:
            print("\n[WARNING] Invalid citation IDs detected.")

    else:
        print("Citation validation data unavailable.")

    # =====================================================
    # RESEARCH API ERRORS
    # =====================================================

    errors = result.get("errors", [])

    if errors:
        print("\n" + "=" * 60)
        print("RESEARCH API WARNINGS")
        print("=" * 60)

        for error in errors:
            print(
                f"[WARNING] {error.get('source', 'Unknown')}: "
                f"{error.get('error', 'Unknown error')}"
            )

    # =====================================================
    # WORKFLOW COMPLETED
    # =====================================================

    print("\n" + "=" * 60)
    print("MULTI-AGENT RESEARCH WORKFLOW FINISHED")
    print("=" * 60)


if __name__ == "__main__":
    main()