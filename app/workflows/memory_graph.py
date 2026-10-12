from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END

from app.workflows.hybrid_graph import hybrid_graph
from app.memory.database import save_research
from app.memory.semantic_memory import (
    search_memory,
    add_research_to_memory,
)
from app.memory.knowledge_graph import save_extraction
from app.services.entity_extractor import (
    extract_entities_and_relationships,
)


class MemoryResearchState(TypedDict, total=False):
    question: str
    use_web: bool
    use_documents: bool
    previous_memories: list
    hybrid_result: dict
    report: str
    research_id: int
    memory_index_result: dict
    knowledge_extraction: dict
    errors: list


def retrieve_memory_agent(state: MemoryResearchState):
    """Retrieve related previous research."""

    print("\n[1/4] Research Memory Retrieval")

    try:
        memories = search_memory(
            state["question"],
            top_k=3,
            min_score=0.35,
        )

        print(f"Related memories found: {len(memories)}")

        return {"previous_memories": memories}

    except Exception as exc:
        return {
            "previous_memories": [],
            "errors": [f"Memory retrieval failed: {exc}"],
        }


def hybrid_research_agent(state: MemoryResearchState):
    question = state["question"].strip()

    print("\n[2/4] Hybrid Research Workflow")

    # Keep the search query clean.
    # Previous memories must not be appended to API queries.
    result = hybrid_graph.invoke({
        "question": question,
        "use_web": state.get("use_web", True),
        "use_documents": state.get("use_documents", True),
        "errors": [],
    })

    return {
        "hybrid_result": result,
        "report": result.get("report", ""),
        "errors": (
            state.get("errors", [])
            + result.get("errors", [])
        ),
    }


def save_memory_agent(state: MemoryResearchState):
    """Persist the report and index it semantically."""

    print("\n[3/4] Save Research Memory")

    result = state["hybrid_result"]
    report = state.get("report", "")

    if not report.strip():
        return {
            "errors": state.get("errors", [])
            + ["Cannot save an empty research report"]
        }

    research_id = save_research(
        question=state["question"],
        report=report,
        research_plan=result.get("plan", ""),
        analysis=result.get("analysis", ""),
        evidence=result.get("evidence", []),
        citation_validation=result.get(
            "citation_validation", {}
        ),
    )

    update = {"research_id": research_id}

    try:
        index_result = add_research_to_memory(research_id)
        update["memory_index_result"] = index_result

    except Exception as exc:
        update["errors"] = (
            state.get("errors", [])
            + [f"Semantic indexing failed: {exc}"]
        )

    return update


def knowledge_graph_agent(state: MemoryResearchState):
    """Extract and store knowledge graph information."""

    print("\n[4/4] Knowledge Graph Extraction")

    report = state.get("report", "")

    if not report.strip():
        return {"knowledge_extraction": {
            "entities": [],
            "relationships": [],
        }}

    try:
        extraction = extract_entities_and_relationships(
            report,
            max_characters=12000,
        )

        save_extraction(
            extraction,
            research_id=state.get("research_id"),
        )

        print(
            f"Extracted entities: "
            f"{len(extraction['entities'])}"
        )
        print(
            f"Extracted relationships: "
            f"{len(extraction['relationships'])}"
        )

        return {"knowledge_extraction": extraction}

    except Exception as exc:
        return {
            "knowledge_extraction": {
                "entities": [],
                "relationships": [],
            },
            "errors": state.get("errors", [])
            + [f"Knowledge extraction failed: {exc}"],
        }


builder = StateGraph(MemoryResearchState)

builder.add_node("retrieve_memory", retrieve_memory_agent)
builder.add_node("hybrid_research", hybrid_research_agent)
builder.add_node("save_memory", save_memory_agent)
builder.add_node("knowledge_graph", knowledge_graph_agent)

builder.add_edge(START, "retrieve_memory")
builder.add_edge("retrieve_memory", "hybrid_research")
builder.add_edge("hybrid_research", "save_memory")
builder.add_edge("save_memory", "knowledge_graph")
builder.add_edge("knowledge_graph", END)

memory_graph = builder.compile()