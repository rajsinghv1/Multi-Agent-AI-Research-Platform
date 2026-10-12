import argparse

from app.rag.rag_engine import (
    index_pdf,
    ask_document
)


def main():
    parser = argparse.ArgumentParser(
        description="Phase 5 Document RAG Engine"
    )

    parser.add_argument(
        "--index",
        help="Path to PDF to index"
    )

    parser.add_argument(
        "--ask",
        help="Question to ask indexed documents"
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5
    )

    args = parser.parse_args()

    if args.index:
        result = index_pdf(args.index)
        print("\nINDEXING COMPLETE")
        print(result)

    elif args.ask:
        result = ask_document(
            args.ask,
            top_k=args.top_k
        )

        print("\nDOCUMENT ANSWER\n")
        print(result["answer"])

        print("\nRETRIEVED PASSAGES")

        for i, source in enumerate(
            result["sources"], 1
        ):
            print(
                f"[D{i}] {source['source']} "
                f"page {source['page']} "
                f"score={source['score']:.4f}"
            )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()