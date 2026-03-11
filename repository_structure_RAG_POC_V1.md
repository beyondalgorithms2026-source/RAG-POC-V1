# RAG PoC v1 — Repository Structure

## Directory Tree

```
rag-poc-v1/
├── README.md
├── docker-compose.yml
├── project_plan.md
├── demo_questions.md
├── eval_report*.json          # (7 evaluation report files)
├── .gitignore
│
├── backend/
│   ├── .env / .env.example
│   ├── requirements.txt
│   ├── server_log.txt
│   ├── chunk_snippets_200.csv
│   ├── edgar_001_operating_agreement.pdf
│   ├── edgar_002_exhibit101.pdf
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── search.py
│   │   │   └── ask.py
│   │   │
│   │   ├── answering/
│   │   │   ├── __init__.py
│   │   │   └── ask.py
│   │   │
│   │   ├── chunking/
│   │   │   ├── __init__.py
│   │   │   ├── splitter.py
│   │   │   └── process.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── db.py
│   │   │   ├── schema.sql
│   │   │   ├── migrate.py
│   │   │   ├── verify_db.py
│   │   │   ├── repo_chunks.py
│   │   │   ├── repo_documents.py
│   │   │   ├── repo_embeddings.py
│   │   │   └── repo_search.py
│   │   │
│   │   ├── embedding/
│   │   │   ├── embedder.py
│   │   │   └── process.py
│   │   │
│   │   ├── eval/
│   │   │   ├── __init__.py
│   │   │   └── retrieval_eval.py
│   │   │
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py
│   │   │   ├── parsers.py
│   │   │   ├── file_walker.py
│   │   │   ├── hashing.py
│   │   │   └── normalize.py
│   │   │
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── prompts.py
│   │   │
│   │   └── retrieval/
│   │       ├── __init__.py
│   │       ├── search.py
│   │       └── reranker.py
│   │
│   ├── tests/
│   │   └── test_health.py
│   │
│   └── venv/                  # (virtual environment — not tracked)
│
├── frontend/
│   ├── index.html
│   └── app.js
│
├── data/
│   ├── contracts/             # 20 CUAD PDFs + 1 oneNDA.docx
│   └── extracted_text/        # Plain-text extractions (hash__filename.txt)
│
└── scripts/                   # (empty)
```

---

## File Reference Table

### Root

| File | Folder | Purpose |
|---|---|---|
| [README.md](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/README.md) | `/` | Project overview, setup instructions, CLI commands |
| [docker-compose.yml](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/docker-compose.yml) | `/` | Spins up PostgreSQL + pgvector container |
| [project_plan.md](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/project_plan.md) | `/` | Milestone-based development roadmap |
| [demo_questions.md](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/demo_questions.md) | `/` | 40 grounded eval questions with expected chunk IDs |
| `eval_report*.json` | `/` | Evaluation outputs for vector / keyword / hybrid / rerank modes |
| [.gitignore](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/.gitignore) | `/` | Git ignore rules |

---

### Backend — Core & Config

| File | Folder | Purpose |
|---|---|---|
| [.env](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/.env) / [.env.example](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/.env.example) | `backend/` | Environment variables (DB URL, model names, keys) |
| [requirements.txt](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/requirements.txt) | `backend/` | Python dependency manifest |
| [main.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/main.py) | `backend/app/` | FastAPI app factory — mounts routers, CORS, lifespan LLM check |
| [config.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/core/config.py) | `backend/app/core/` | Pydantic [Settings](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/core/config.py#12-42) class — all env-driven config (DB, embedding model, LLM, reranker, hybrid params) |
| [logging.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/core/logging.py) | `backend/app/core/` | Centralised logger setup |

---

### Backend — API Layer

| File | Folder | Purpose |
|---|---|---|
| [health.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/api/health.py) | `backend/app/api/` | `GET /health` endpoint |
| [search.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/api/search.py) | `backend/app/api/` | `POST /search` — request/response schemas (`SearchRequest`, `SearchResponse`, `SearchResultItem`) + route |
| [ask.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/api/ask.py) | `backend/app/api/` | `POST /ask` — RAG Q&A route with request/response schemas |

---

### Backend — Ingestion Pipeline

| File | Folder | Purpose |
|---|---|---|
| [ingest.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/cli_ingest.py) | `backend/app/ingestion/` | Orchestrator — walks data dir, hashes, parses, normalises, upserts documents into DB |
| [parsers.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/ingestion/parsers.py) | `backend/app/ingestion/` | PDF / DOCX text extraction logic |
| [file_walker.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/ingestion/file_walker.py) | `backend/app/ingestion/` | Recursively finds supported files in a directory |
| [hashing.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/ingestion/hashing.py) | `backend/app/ingestion/` | SHA-256 file hashing for dedup |
| [normalize.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/ingestion/normalize.py) | `backend/app/ingestion/` | Text cleanup / whitespace normalisation |
| [cli_ingest.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/cli_ingest.py) | `backend/app/` | CLI entry point: `python -m app.cli_ingest` |

---

### Backend — Chunking

| File | Folder | Purpose |
|---|---|---|
| [splitter.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/chunking/splitter.py) | `backend/app/chunking/` | Heading-aware 3-pass text splitter (section split → paragraph split → packing) with overlap |
| [process.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/chunking/process.py) | `backend/app/chunking/` | Orchestrator — reads extracted text, calls [split_text](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/chunking/splitter.py#37-167), writes chunks to DB |
| [cli_chunk.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/cli_chunk.py) | `backend/app/` | CLI entry point: `python -m app.cli_chunk` |

---

### Backend — Embedding

| File | Folder | Purpose |
|---|---|---|
| [embedder.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/embedding/embedder.py) | `backend/app/embedding/` | `embed_texts()` — wraps `sentence-transformers` model (`BAAI/bge-small-en-v1.5` default) |
| [process.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/chunking/process.py) | `backend/app/embedding/` | Orchestrator — batch-embeds un-embedded chunks, stores vectors in DB |
| [cli_embed.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/cli_embed.py) | `backend/app/` | CLI entry point: `python -m app.cli_embed` |

---

### Backend — Database / Repositories

| File | Folder | Purpose |
|---|---|---|
| [db.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/db.py) | `backend/app/db/` | SQLAlchemy `engine` singleton |
| [schema.sql](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/schema.sql) | `backend/app/db/` | DDL for [documents](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/ingestion/ingest.py#22-102), [chunks](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/repo_search.py#7-84) tables (pgvector + tsvector columns) |
| [migrate.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/migrate.py) | `backend/app/db/` | Schema migration / setup runner |
| [verify_db.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/verify_db.py) | `backend/app/db/` | Post-setup DB verification checks |
| [repo_documents.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/repo_documents.py) | `backend/app/db/` | CRUD helpers for the [documents](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/ingestion/ingest.py#22-102) table |
| [repo_chunks.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/repo_chunks.py) | `backend/app/db/` | CRUD helpers for the [chunks](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/repo_search.py#7-84) table |
| [repo_embeddings.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/repo_embeddings.py) | `backend/app/db/` | Helpers for reading/writing vector embeddings on chunks |
| [repo_search.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/repo_search.py) | `backend/app/db/` | [search_chunks()](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/repo_search.py#7-84) (pgvector cosine) + [search_chunks_keyword()](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/db/repo_search.py#85-169) (tsvector `ts_rank_cd`) with filter support |

---

### Backend — Retrieval

| File | Folder | Purpose |
|---|---|---|
| [search.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/api/search.py) | `backend/app/retrieval/` | [perform_search()](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/retrieval/search.py#83-203) — orchestrates vector / keyword / hybrid mode; [merge_hybrid_results()](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/retrieval/search.py#9-82) — RRF-style fusion with alpha weighting |
| [reranker.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/retrieval/reranker.py) | `backend/app/retrieval/` | Cross-encoder reranker (`ms-marco-MiniLM-L-6-v2`) post-processing step |

---

### Backend — LLM

| File | Folder | Purpose |
|---|---|---|
| [client.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/llm/client.py) | `backend/app/llm/` | [verify_llm_ready()](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/llm/client.py#20-76) preflight + [generate_answer()](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/llm/client.py#77-142) — supports Ollama local + Ollama Cloud providers |
| [prompts.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/llm/prompts.py) | `backend/app/llm/` | System / user prompt templates for RAG answer generation |

---

### Backend — Answering

| File | Folder | Purpose |
|---|---|---|
| [ask.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/api/ask.py) | `backend/app/answering/` | End-to-end RAG pipeline — search → build context → LLM call → structured JSON response |

---

### Backend — Evaluation

| File | Folder | Purpose |
|---|---|---|
| [retrieval_eval.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/app/eval/retrieval_eval.py) | `backend/app/eval/` | CLI evaluation harness — parses [demo_questions.md](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/demo_questions.md), runs retrieval, computes hit@k / MRR, outputs JSON report |

---

### Backend — Tests

| File | Folder | Purpose |
|---|---|---|
| [test_health.py](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/tests/test_health.py) | `backend/tests/` | Smoke test for the `/health` endpoint |

---

### Frontend

| File | Folder | Purpose |
|---|---|---|
| [index.html](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/frontend/index.html) | `frontend/` | Single-page UI — search form, results display, ask panel |
| [app.js](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/frontend/app.js) | `frontend/` | Frontend logic — API calls to `/search` and `/ask`, DOM rendering |

---

### Data

| File | Folder | Purpose |
|---|---|---|
| `cuad_001…020.pdf` | `data/contracts/` | 20 CUAD benchmark legal contracts (source PDFs) |
| [oneNDA.docx](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/data/contracts/oneNDA.docx) | `data/contracts/` | Sample NDA document (DOCX format) |
| `*__.txt` | `data/extracted_text/` | Auto-generated plain-text extractions, one per ingested document |

---

### Misc

| File | Folder | Purpose |
|---|---|---|
| [chunk_snippets_200.csv](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/chunk_snippets_200.csv) | `backend/` | Pre-exported chunk CSV used to ground evaluation questions |
| `edgar_001/002*.pdf` | `backend/` | Additional test PDFs (SEC EDGAR filings) |
| [server_log.txt](file:///Users/Work/local_dev/RAG%20workflow/rag-poc-v1/rag-poc-v1/backend/server_log.txt) | `backend/` | Server startup log snapshot |
