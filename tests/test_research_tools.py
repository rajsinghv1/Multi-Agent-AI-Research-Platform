from app.tools.research_tools import collect_research


def test_research_tools():
    query = "retrieval augmented generation"

    print("\nTesting research tools...")

    result = collect_research(query)

    assert isinstance(result, dict)
    assert "sources" in result
    assert "errors" in result
    assert "total_sources" in result

    assert (
        result["total_sources"]
        == len(result["sources"])
    )

    for source in result["sources"]:
        assert source.get("source")
        assert source.get("title")
        assert source.get("url")

    assert result["total_sources"] > 0, (
        "No sources retrieved. "
        f"Errors: {result['errors']}"
    )

    print("\nRESEARCH TOOL TEST PASSED")
    print(
        "Total sources:",
        result["total_sources"]
    )

    for source in result["sources"][:5]:
        print(
            f"- [{source['source']}] "
            f"{source['title']}"
        )


if __name__ == "__main__":
    test_research_tools()