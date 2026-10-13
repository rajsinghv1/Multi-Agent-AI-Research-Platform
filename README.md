# Multi-Agent AI Research Platform

A local-first, multi-agent research assistant built with **Python, LangGraph, Google Gemini, Streamlit, FAISS and SQLite**. It combines academic search with PDF retrieval-augmented generation (RAG), produces citation-aware research reports, and stores research history and extracted knowledge relationships.

> **Project status:** Core PDF-only and hybrid research pipelines have been exercised locally. Streamlit end-to-end testing, report quality, and deployment readiness should be verified before describing this as production-ready. Google Gemini API quotas apply.

## Features

- LangGraph research workflow: planning, retrieval, evidence fusion, analysis, report generation
- Academic search using arXiv, Wikipedia and Crossref
- Multi-PDF text extraction, chunking, Gemini embeddings and FAISS similarity search
- PDF-only or combined academic-web + PDF evidence retrieval
- Citation-aware report generation and citation validation
- SQLite research history, semantic memory and knowledge graph extraction
- Streamlit dashboard for research, history, evaluation and export

## Architecture

```text
Streamlit UI (app.py)
        |
        v
LangGraph memory_graph
        |
        +-- Retrieve prior research memory
        +-- Hybrid research graph
        |      +-- Planning agent (Gemini)
        |      +-- Academic search (arXiv/Wikipedia/Crossref)
        |      +-- PDF retrieval (Gemini embeddings + FAISS)
        |      +-- Evidence fusion
        |      +-- Analysis agent (Gemini)
        |      +-- Report agent (Gemini)
        +-- Save report to SQLite
        +-- Extract knowledge graph entities/relations
```

## Prerequisites

- Windows PowerShell, macOS or Linux terminal
- Python compatible with project dependencies (tested locally by developer with Python 3.12)
- Google Gemini API key and available quota
- Internet for Gemini calls and academic research APIs

## Installation (Windows PowerShell)

```powershell
git clone https://github.com/rajsinghv1/Multi-Agent-AI-Research-Platform.git
cd Multi-Agent-AI-Research-Platform
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` and retry activation.

## Configuration

Create a `.env` file in the project root. Check `app/core/config.py` for the exact required setting names and supported defaults. The project uses `GOOGLE_API_KEY`, `GEMINI_MODEL`, and `GEMINI_TEMPERATURE` in its Gemini client configuration.

Example (adjust model name to one supported by your account):

```dotenv
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.3
```

Never commit `.env`, API keys, uploaded PDFs or local vector databases. The free-tier request quota varies by model/project; a single multi-agent research run can make several generation calls.

## Run locally

```powershell
python -m streamlit run app.py
```

Open http://localhost:8501. Upload and index PDFs on the PDF Research page before asking PDF-grounded questions. For hybrid research, enable both web and document sources.

## Offline tests (no Gemini requests)

```powershell
pip install pytest
python -m pytest tests/test_phase10_offline.py -v
```

For the full existing test suite:

```powershell
python -m pytest tests -q
```

The new offline tests mock external calls. They verify orchestration and interfaces, **not** factual correctness of generated reports. Run a separate manual end-to-end test when API quota is available.

## Manual smoke test

1. Start Streamlit and confirm the dashboard loads.
2. Upload a text-based PDF and index it.
3. Ask a PDF-only question; verify retrieved passages and page references.
4. Enable PDF + Web research; verify both source types are represented.
5. Check research history, citation validation and exports.
6. Confirm Gemini quota errors show a helpful message rather than crashing the entire interface.

## Project structure

```text
app.py                         # Streamlit interface
app/core/                     # Gemini client and settings
app/workflows/                # LangGraph workflows
app/tools/                    # Academic research tools
app/services/                 # Evidence fusion and citations
app/rag/                      # PDF loader, embeddings, FAISS store
app/memory/                   # SQLite and knowledge graph
app/evaluation/               # Research quality evaluation
tests/                        # Automated tests
data/                         # Local files (gitignored)
```

## Troubleshooting

- **429 RESOURCE_EXHAUSTED:** Check the model's quota in Google AI Studio. Wait for reset or use a model with available quota; repeated retries will not restore a daily allowance.
- **No PDF passages:** Confirm PDF indexing succeeded, the document contains extractable text, and the same FAISS store is used for retrieval.
- **arXiv HTTP 500:** Retry later and keep API search queries limited to the original question; do not append prior report excerpts.
- **Missing module:** Activate the virtual environment and install `requirements.txt`.
- **FAISS index mismatch:** Verify metadata and index integrity; back up local data before rebuilding.

## Security and privacy

PDF uploads and research history are stored locally. Avoid uploading confidential documents to external AI services without authorization. Gemini embeddings and report generation send relevant text to Google APIs. Treat retrieved web/PDF content as untrusted input and validate generated citations before relying on them.

## Deployment notes

This project is designed for local execution. For deployment, use an appropriate secret manager for the Gemini key, configure persistent storage for SQLite/FAISS, set upload limits, add authentication for multi-user access, and review data retention. Do not deploy as a public multi-user service without those controls.


## License

Add a `LICENSE` file before stating that the repository is open-source under a specific license.
