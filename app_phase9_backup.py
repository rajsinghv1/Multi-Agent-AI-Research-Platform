
import json

import streamlit as st

from app.memory.database import (
    init_database,
    get_research,
    list_research,
)
from app.evaluation.unified_evaluator import evaluate_research
from app.evaluation.report_comparison import compare_reports
from app.phase8_cli import build_markdown


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Multi-Agent AI Research Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

@st.cache_resource(show_spinner=False)
def initialize_database():
    init_database()
    return True


initialize_database()


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def load_research(research_id):
    return get_research(int(research_id))


def get_report(research):
    if not research:
        return ""

    if isinstance(research, dict):
        return research.get("report", "") or ""

    try:
        return research["report"] or ""
    except (KeyError, IndexError, TypeError):
        return ""


def get_research_ids():
    records = list_research()

    if not records:
        return []

    ids = []

    for record in records:
        if isinstance(record, dict):
            research_id = record.get("id")
        else:
            try:
                research_id = record["id"]
            except (KeyError, IndexError, TypeError):
                continue

        if research_id is not None:
            ids.append(int(research_id))

    return ids


def run_evaluation(report):
    return evaluate_research(report)


def download_json(label, data, filename):
    st.download_button(
        label=label,
        data=json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        file_name=filename,
        mime="application/json",
        width="stretch",
    )


# ==========================================================
# HEADER
# ==========================================================

st.title("🔬 Multi-Agent AI Research Platform")

st.caption(
    "Google Gemini | LangGraph | PDF RAG | "
    "FAISS | Research Intelligence"
)

st.divider()


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.header("Navigation")

    page = st.radio(
        "Select Module",
        [
            "Dashboard",
            "Research History",
            "Research Evaluation",
            "Compare Reports",
            "Export Reports",
        ],
    )

    st.divider()

    st.subheader("Platform Status")

    st.success("Research Database Initialized")

    st.info("LLM Provider: Google Gemini")

    st.caption(
        "Offline evaluation works without Gemini API calls."
    )


# ==========================================================
# DASHBOARD
# ==========================================================

if page == "Dashboard":

    st.header("Research Intelligence Dashboard")

    ids = get_research_ids()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Saved Research",
        len(ids),
    )

    col2.metric(
        "Evaluation Modules",
        5,
    )

    col3.metric(
        "LLM Provider",
        "Gemini",
    )

    col4.metric(
        "Research Storage",
        "SQLite",
    )

    st.divider()

    st.subheader("Available Features")

    st.markdown(
        """
        ### Research Engine
        - LangGraph Multi-Agent Research
        - Google Gemini LLM
        - arXiv Research
        - Wikipedia Research
        - Crossref Research

        ### Knowledge Intelligence
        - PDF RAG with FAISS
        - Persistent Research Memory
        - Knowledge Graph
        - Semantic Memory

        ### Research Evaluation
        - Research Quality Scoring
        - Contradiction Detection
        - Source Credibility Analysis
        - Research Gap Identification
        - Multi-Report Comparison
        - JSON and Markdown Export
        """
    )

    st.info(
        "Research generation and PDF upload UI "
        "will be integrated in the next steps."
    )


# ==========================================================
# RESEARCH HISTORY
# ==========================================================

elif page == "Research History":

    st.header("Saved Research History")

    ids = get_research_ids()

    if not ids:
        st.warning("No saved research reports found.")

    else:
        selected_id = st.selectbox(
            "Select Research ID",
            ids,
        )

        research = load_research(selected_id)

        if research:
            report = get_report(research)

            st.subheader(
                f"Research Report #{selected_id}"
            )

            if report.strip():
                st.markdown(report)
            else:
                st.warning("Research report is empty.")

            st.download_button(
                "Download Research Report",
                data=report,
                file_name=f"research_{selected_id}.md",
                mime="text/markdown",
                width="stretch",
            )

        else:
            st.error("Research record not found.")


# ==========================================================
# RESEARCH EVALUATION
# ==========================================================

elif page == "Research Evaluation":

    st.header("Research Quality Evaluation")

    ids = get_research_ids()

    if not ids:
        st.warning("No saved research available.")

    else:
        selected_id = st.selectbox(
            "Select Research ID",
            ids,
        )

        if st.button(
            "Evaluate Research",
            type="primary",
            width="stretch",
        ):
            research = load_research(selected_id)

            if research:
                report = get_report(research)

                with st.spinner(
                    "Evaluating research quality..."
                ):
                    result = run_evaluation(report)

                st.session_state["evaluation_result"] = result
                st.session_state["evaluation_id"] = selected_id

            else:
                st.error("Research not found.")

        if (
            "evaluation_result" in st.session_state
            and st.session_state.get("evaluation_id")
            == selected_id
        ):
            result = st.session_state["evaluation_result"]

            quality = result["quality"]
            gaps = result["research_gaps"]

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Quality Score",
                f"{quality['overall_score']}/100",
            )

            col2.metric(
                "Quality Grade",
                quality["grade"],
            )

            col3.metric(
                "Research Gap Matches",
                gaps["total_explicit_gaps"],
            )

            st.divider()

            st.subheader("Detailed Evaluation")

            st.json(result)

            download_json(
                "Download Evaluation JSON",
                result,
                f"research_{selected_id}_evaluation.json",
            )

            st.caption(
                "Scores and findings are heuristic. "
                "They do not independently verify factual accuracy."
            )


# ==========================================================
# COMPARE REPORTS
# ==========================================================

elif page == "Compare Reports":

    st.header("Multi-Report Comparison")

    ids = get_research_ids()

    if len(ids) < 2:
        st.warning(
            "At least two saved research reports "
            "are required for comparison."
        )

    else:
        col1, col2 = st.columns(2)

        with col1:
            first_id = st.selectbox(
                "First Research Report",
                ids,
                key="first_report",
            )

        with col2:
            second_id = st.selectbox(
                "Second Research Report",
                ids,
                index=1,
                key="second_report",
            )

        if st.button(
            "Compare Reports",
            type="primary",
            width="stretch",
        ):

            if first_id == second_id:
                st.warning(
                    "Please select two different reports."
                )

            else:
                first = load_research(first_id)
                second = load_research(second_id)

                if not first or not second:
                    st.error(
                        "One or both research reports are missing."
                    )
                else:
                    result = compare_reports(
                        get_report(first),
                        get_report(second),
                    )

                    st.session_state["comparison_result"] = result
                    st.session_state["comparison_ids"] = (
                        first_id,
                        second_id,
                    )

        if (
            st.session_state.get("comparison_ids")
            == (first_id, second_id)
            and "comparison_result" in st.session_state
        ):
            result = st.session_state["comparison_result"]

            st.metric(
                "Keyword Similarity",
                f"{result['similarity_score']}%",
            )

            st.progress(
                min(
                    max(result["similarity_score"] / 100, 0),
                    1,
                )
            )

            st.subheader("Comparison Details")

            st.json(result)

            download_json(
                "Download Comparison JSON",
                result,
                f"comparison_{first_id}_{second_id}.json",
            )


# ==========================================================
# EXPORT REPORTS
# ==========================================================

elif page == "Export Reports":

    st.header("Research Report Export Center")

    ids = get_research_ids()

    if not ids:
        st.warning("No saved reports available.")

    else:
        selected_id = st.selectbox(
            "Select Research ID",
            ids,
        )

        research = load_research(selected_id)

        if research:
            report = get_report(research)

            result = run_evaluation(report)

            markdown = build_markdown(
                selected_id,
                result,
            )

            st.subheader("Export Options")

            st.download_button(
                "Download Original Research",
                data=report,
                file_name=f"research_{selected_id}.md",
                mime="text/markdown",
                width="stretch",
            )

            st.download_button(
                "Download Evaluation Markdown",
                data=markdown,
                file_name=(
                    f"research_{selected_id}_evaluation.md"
                ),
                mime="text/markdown",
                width="stretch",
            )

            download_json(
                "Download Evaluation JSON",
                result,
                f"research_{selected_id}_evaluation.json",
            )

            with st.expander("Preview Evaluation Markdown"):
                st.code(
                    markdown,
                    language="markdown",
                )

        else:
            st.error("Research record not found.")


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "Multi-Agent AI Research & Knowledge Intelligence Platform "
    "| Phase 9 | Local Development"
)
