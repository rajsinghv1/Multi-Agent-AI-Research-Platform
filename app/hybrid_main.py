import argparse

from app.rag.multi_document_store import (
    index_document,
)
from app.workflows.hybrid_graph import (
    hybrid_graph,
)


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Hybrid Research Platform"
    )

    parser.add_argument(
        "--index",
        help="Index a PDF document"
    )

    parser.add_argument(
        "--question",
        help="Research question"
    )

    parser.add_argument(
        "--no-web",
        action="store_true",
        help="Disable academic API research"
    )

    parser.add_argument(
        "--no-documents",
        action="store_true",
        help="Disable local document retrieval"
    )

    args = parser.parse_args()

    if args.index:
        result = index_document(args.index)

        print("\nDOCUMENT INDEXING RESULT")
        print(result)
        return

    question = args.question

    if not question:
        question = input(
            "Enter research question: "
        ).strip()

    if not question:
        parser.error("A research question is required")

    state = {
        "question": question,
        "plan": "",
        "research_data": {},
        "evidence": [],
        "analysis": "",
        "report": "",
        "citation_validation": {},
        "errors": [],
        "use_web": not args.no_web,
        "use_documents": not args.no_documents,
    }

    result = hybrid_graph.invoke(state)

    print("\n" + "=" * 60)
    print("FINAL HYBRID RESEARCH REPORT")
    print("=" * 60)

    print(result["report"])

    print("\n" + "=" * 60)
    print("EVIDENCE SOURCES")
    print("=" * 60)

    for item in result["evidence"]:
        if item["type"] == "web":
            print(
                f"[{item['citation']}] "
                f"{item['title']}\n"
                f"URL: {item['url']}"
            )
        else:
            print(
                f"[{item['citation']}] "
                f"{item['title']} "
                f"page {item['page']}"
            )

    print("\nCITATION VALIDATION")
    print(result["citation_validation"])

    if result["errors"]:
        print("\nRETRIEVAL WARNINGS")

        for error in result["errors"]:
            print("-", error)


if __name__ == "__main__":
    main()