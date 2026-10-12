import argparse
import json

from app.memory.database import (
    get_research,
    list_research,
    search_research,
)
from app.memory.knowledge_graph import (
    get_entities,
    get_relationships,
    get_graph_stats,
)
from app.memory.semantic_memory import (
    get_memory_stats,
    search_memory,
)


def show_history(limit=10):
    records = list_research(limit=limit)

    if not records:
        print("No saved research found.")
        return

    for record in records:
        print(f"ID: {record['id']}")
        print(f"Question: {record['question']}")
        print("-" * 50)


def show_research(research_id):
    record = get_research(research_id)

    if record is None:
        print(f"Research ID {research_id} not found.")
        return

    print(f"Question: {record['question']}")
    print("\nREPORT:\n")
    print(record["report"])


def keyword_search(keyword, limit=10):
    records = search_research(keyword, limit=limit)

    if not records:
        print("No matching research found.")
        return

    for record in records:
        print(f"ID: {record['id']}")
        print(f"Question: {record['question']}")


def show_entities(limit=100):
    entities = get_entities(limit=limit)
    print(json.dumps(entities, indent=2, default=str))


def show_relationships(entity=None, limit=100):
    relationships = get_relationships(
        entity_name=entity,
        limit=limit,
    )
    print(json.dumps(relationships, indent=2, default=str))


def show_stats():
    print("\nKnowledge Graph:")
    print(json.dumps(get_graph_stats(), indent=2))

    print("\nSemantic Memory:")
    print(json.dumps(get_memory_stats(), indent=2))


def semantic_search(question, top_k=5):
    results = search_memory(question, top_k=top_k)
    print(json.dumps(results, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Research Platform CLI"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    history = subparsers.add_parser("history")
    history.add_argument("--limit", type=int, default=10)

    report = subparsers.add_parser("report")
    report.add_argument("--id", type=int, required=True)

    keyword = subparsers.add_parser("keyword")
    keyword.add_argument("--query", required=True)

    entities = subparsers.add_parser("entities")
    entities.add_argument("--limit", type=int, default=100)

    relationships = subparsers.add_parser("relationships")
    relationships.add_argument("--entity", default=None)

    subparsers.add_parser("stats")

    semantic = subparsers.add_parser("semantic")
    semantic.add_argument("--query", required=True)
    semantic.add_argument("--top-k", type=int, default=5)

    args = parser.parse_args()

    if args.command == "history":
        show_history(args.limit)

    elif args.command == "report":
        show_research(args.id)

    elif args.command == "keyword":
        keyword_search(args.query)

    elif args.command == "entities":
        show_entities(args.limit)

    elif args.command == "relationships":
        show_relationships(args.entity)

    elif args.command == "stats":
        show_stats()

    elif args.command == "semantic":
        semantic_search(args.query, args.top_k)


if __name__ == "__main__":
    main()