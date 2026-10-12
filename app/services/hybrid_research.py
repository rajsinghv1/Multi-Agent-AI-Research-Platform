from app.tools.research_tools import collect_research
from app.rag.multi_document_store import search_documents
from app.services.evidence_fusion import fuse_evidence


def collect_hybrid_research(
    question,
    use_web=True,
    use_documents=True,
    top_k=5
):
    web_sources = []
    document_sources = []
    errors = []
    web_metrics = {}

    if use_web:
        try:
            result = collect_research(question)

            web_sources = result.get("sources", [])
            web_metrics = result.get("metrics", {})

            errors.extend(
                str(error)
                for error in result.get("errors", [])
            )

        except Exception as exc:
            errors.append(
                f"Academic research failed: {exc}"
            )

    if use_documents:
        try:
            document_sources = search_documents(
                question,
                top_k=top_k
            )

        except Exception as exc:
            errors.append(
                f"Document retrieval failed: {exc}"
            )

    evidence = fuse_evidence(
        web_sources,
        document_sources
    )

    return {
        "evidence": evidence,
        "web_count": sum(
            item["type"] == "web"
            for item in evidence
        ),
        "document_count": sum(
            item["type"] == "document"
            for item in evidence
        ),
        "errors": errors,
        "web_metrics": web_metrics,
    }