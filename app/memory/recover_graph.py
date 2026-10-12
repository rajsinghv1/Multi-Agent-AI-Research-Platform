import argparse
import json

from app.core.llm import GeminiQuotaExceeded
from app.memory.database import get_research
from app.memory.knowledge_graph import (
    save_extraction,
    get_graph_stats,
)
from app.services.entity_extractor import (
    extract_entities_and_relationships,
)


def recover_knowledge_graph(research_id: int):
    research = get_research(research_id)

    if research is None:
        print(f"[ERROR] Research ID {research_id} not found.")
        return None

    print(f"\n[OK] Research ID: {research_id}")
    print(f"Question: {research['question']}")

    try:
        print("\n[INFO] Extracting entities and relationships...")

        extraction = extract_entities_and_relationships(
            research["report"]
        )

    except GeminiQuotaExceeded:
        print("\n[WARNING] Gemini daily quota exhausted.")
        print("[INFO] Knowledge graph recovery postponed.")
        print("[INFO] Your saved research is safe.")
        print("[INFO] Retry after Google's quota resets.")
        return None

    except Exception as exc:
        print(f"\n[ERROR] Knowledge extraction failed: {exc}")
        return None

    try:
        save_extraction(
            extraction,
            research_id=research_id,
        )

        print("\n[SUCCESS] Knowledge graph updated!")

        print("\nExtracted knowledge:")
        print(json.dumps(extraction, indent=2))

        print("\nKnowledge graph statistics:")
        print(json.dumps(get_graph_stats(), indent=2))

        return extraction

    except Exception as exc:
        print(f"\n[ERROR] Could not save knowledge graph: {exc}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Recover knowledge graph from saved research"
    )

    parser.add_argument(
        "--research-id",
        type=int,
        required=True,
    )

    args = parser.parse_args()

    result = recover_knowledge_graph(args.research_id)

    if result is None:
        print("\n[INFO] Recovery incomplete.")
        print("[INFO] No saved research was deleted.")


if __name__ == "__main__":
    main()