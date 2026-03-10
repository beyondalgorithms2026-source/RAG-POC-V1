# RAG PoC v1 — Contracts Q&A with Citations (Project Plan)

## 1) Objective and non-goals
### Objective
Build a **minimal but credible RAG system** for a **single team** to ask questions over a **single folder of contracts** (PDF/DOCX) and receive:
- a concise answer
- **citations to exact source chunks**
- basic filters (doc type + contract date)

This is the smallest build that proves the workflow end-to-end:
**Ingest → Chunk → Embed → Store → Retrieve → Answer → Cite → UI**

### Non-goals
- Scanned/image-only PDFs (unless we add OCR later)
- Org-wide permissions / SSO / document-level ACL mirroring
- Multi-system sync (SharePoint/Drive/Confluence/Jira/CRM)
- Strong compliance guarantees (audit-grade governance)
- High concurrency / high QPS (this is a PoC)
- Tool actions (creating tickets, updating CRM, approvals)

## 2) Scope
### Target user group
One function/team: **Legal / Contracts** (best-quality documents; easiest win)

### Document set
- ~500 contracts in a single folder
- Formats: PDF + DOCX (clean, text-based preferred)

### Supported queries (v1)
- Clause Q&A: termination, governing law, payment terms, indemnity, limitation of liability
- “Find” style: return top relevant sections with citations
- Filters:
  - `doc_type` (pdf/docx)
  - `contract_date_from/to` (optional, best-effort extraction)

## 3) Success criteria and acceptance tests
### Functional
- Ingest folder and index all documents into Postgres+pgvector
- Query returns top-k relevant chunks
- LLM answers **using only retrieved chunks**
- UI shows answer + citations (file + heading/section + snippet)
- Filters work (doc type, date range)

### Quality
- On a curated demo set of 20–30 questions, at least:
  - **Most answers cite relevant contract sections**
  - When evidence is missing, system says “Not found in provided sources”

### Operational
- Re-running ingestion does **not** re-embed unchanged files (hash-based skip)
- Basic logs exist for ingest counts, errors per file, query latency

## 4) Architecture
### Tech Stack
- **Parsing**: Unstructured or Docling
- **Embeddings**: `sentence-transformers` with `BAAI/bge-small-en-v1.5` (local, 384 dims)
- **Storage**: Postgres + pgvector (via Docker Compose)
- **Backend**: FastAPI (Python)
- **LLM**: Cloud LLM or local via Ollama (`LLM_PROVIDER` abstraction)
- **Frontend**: Minimal web UI (Next.js or simple HTML+fetch)

### Runtime Flow
1. **UI**: User question (+ optional filters)
2. **Backend**: Embed question locally
3. **Retrieve**: Fetch top-k chunks from Postgres/pgvector (+ filters)
4. **LLM**: Provide chunks to LLM with strict grounding rules
5. **Citations**: Return answer + structured citations
6. **UI**: Render answer + clickable citation cards

### Ingestion Flow
1. **Ingest**: Walk local data folder
2. **Hash**: Hash files for change detection
3. **Parse**: Extract clean text + metadata
4. **Chunk**: Split by heading/section (fallback: paragraphs)
5. **Embed**: Create local embeddings for chunks
6. **Store**: Save docs, chunks, and vectors in Postgres

## 5) Detailed step-by-step plan with milestones and substeps
### M0 — Project bootstrap (foundation)
**Goal:** Repo exists, env runs locally, DB is up.
**Steps:**
- [ ] Create repo and folder structure
- [ ] Add docker-compose for Postgres+pgvector
- [ ] Create backend skeleton (FastAPI hello world)
- [ ] Add `.env.example` with config keys
- [ ] Add README with run commands
**Definition of Done:** `docker compose up` starts DB; Backend starts and serves `/health`.

### M1 — Database schema + migrations
**Goal:** Postgres schema ready for docs/chunks/embeddings.
**Steps:**
- [ ] Enable pgvector extension
- [ ] Create `documents` and `chunks` tables
- [ ] Add vector index (HNSW preferred if available)
- [ ] Add basic filter indexes
**Definition of Done:** Can insert 1 dummy doc and 3 dummy chunks; Vector query returns nearest neighbors.

### M2 — Ingestion pipeline v1 (parse + normalize)
**Goal:** Convert PDF/DOCX → clean text + minimal metadata.
**Steps:**
- [ ] Implement folder walker
- [ ] Compute sha256 per file (skip unchanged)
- [ ] Parse DOCX (direct text) and PDF (Unstructured/Docling)
- [ ] Normalize text: whitespace cleanup, remove obvious headers/footers, de-hyphenate line breaks
- [ ] Store document record in DB
**Definition of Done:** Ingest 10 files end-to-end without crash; Logs show processed / skipped / failed counts.

### M3 — Chunking v1 (by heading/section)
**Goal:** Split text into meaningful contract chunks.
**Steps:**
- [ ] Detect headings if parser provides structure
- [ ] Chunk rules: heading-based boundaries (fallback: paragraphs), target ~300–800 tokens, small overlap
- [ ] Store chunks in DB (without embeddings first)
**Definition of Done:** Sample contract chunking shows clear clause groupings; text is not broken mid-sentence too often.

### M4 — Embeddings v1 (local) + indexing
**Goal:** Embed all chunks locally and store vectors.
**Steps:**
- [ ] Load local embedding model (bge-small-en-v1.5)
- [ ] Embed chunk_text → vector(384)
- [ ] Update chunk rows with embeddings
- [ ] Verify vector index performance
**Definition of Done:** Known clause query returns expected section in top results; Dimension matches DB.

### M5 — Retrieval API v1 (pgvector + filters)
**Goal:** Query embedding → top-k chunks with metadata.
**Steps:**
- [ ] API endpoint: `POST /search`
- [ ] Input: question, doc_type, date_from, date_to
- [ ] Embed question locally
- [ ] SQL query: vector cosine distance order + join documents for filters
- [ ] Return list of chunks with file_name, heading, section_path, snippet, score
**Definition of Done:** Endpoint returns stable results; Filters accurately change result set.

### M6 — Answer API v1 (LLM + citations)
**Goal:** LLM answers strictly from retrieved chunks, returns citations.
**Steps:**
- [ ] API endpoint: `POST /ask`
- [ ] Flow: call retrieval (top 10–20) → compose strict prompt
  - Prompt rules: "Answer only from provided sources", "If not found, say not found", "Cite every claim with [S#]", "Do not invent contract terms"
- [ ] Return JSON: answer_text + citations list (source_id, file_name, heading, snippet)
**Definition of Done:** Answers contain citations; Assitant explicitly says "not found" when context is missing.

### M7 — Web UI v1
**Goal:** Simple interface that feels real to a client.
**Steps:**
- [ ] Input box + Ask button
- [ ] Filters for doc type + date range
- [ ] Render answer + citation cards (file name, heading, snippet, expand to full chunk)
**Definition of Done:** Usable in < 60 seconds by non-technical user; Citations are prominent and clickable.

### M8 — Demo pack + basic evaluation
**Goal:** PoC is demoable and measurable.
**Steps:**
- [ ] Create demo questions script
- [ ] Add eval script (check for citations, expected contract sections)
- [ ] Document known limitations
**Definition of Done:** Repeatable demo runs smoothly; Simple retrieval accuracy metrics can be shown.

### M8.1 — Corpus expansion (EDGAR contracts) + eval compare (baseline vs rerank)
**Goal:** Grow corpus fast with real contracts and measure retrieval improvements with/without reranker.

**Dataset (tested source):**
- Hugging Face dataset: `chenghao/sec-material-contracts-qa` (800+ EDGAR contracts with PDF images + extracted fields).  [oai_citation:2‡huggingface.co](https://huggingface.co/datasets/chenghao/sec-material-contracts-qa?utm_source=chatgpt.com)

**Steps:**
- [ ] Download a small, deterministic subset of PDFs into `data/contracts/` (e.g., first 20 items or a pinned list)
- [ ] Run pipeline: ingest → chunk → embed
- [ ] Run M8 eval twice and save reports:
  - baseline: `RERANK_ENABLED=false`
  - rerank: `RERANK_ENABLED=true`
- [ ] Compare:
  - pass_rate delta
  - failures list delta
  - best_match_rank shifts (where available)

**Definition of Done:**
- At least 10 PDFs added to corpus
- Two reports exist side-by-side: `eval_report_baseline.json` and `eval_report_rerank.json`
- README documents exact commands to reproduce the run

## 6) Repo structure
```text
rag-poc-v1/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── ingestion/    # parsing, cleaning, chunking
│   │   ├── retrieval/    # pgvector queries, filters
│   │   ├── llm/          # LLM interface + prompts
│   │   ├── db/           # schema, migrations, db utils
│   │   ├── core/         # config, logging
│   ├── tests/
│   ├── pyproject.toml / requirements.txt
│   └── .env.example
├── frontend/             # Next.js app or static files
├── data/
│   └── contracts/        # ignored by git
├── docker-compose.yml    # postgres + pgvector
├── PROJECT_PLAN.md       # this file
└── README.md
```

## 7) Config and env vars
- `DATABASE_URL=postgresql://...`
- `EMBEDDING_MODEL=BAAI/bge-small-en-v1.5`
- `EMBEDDING_DIM=384`
- `LLM_PROVIDER=cloud|local`
- `LLM_MODEL=...`
- `DATA_DIR=./data/contracts`
- `TOP_K=10`
- `MAX_CONTEXT_CHUNKS=8`

## 8) Data model (Postgres schema overview)
### Tables
- `documents`: id, file_path, file_name, doc_type, contract_date (optional), sha256_hash
- `chunks`: id, document_id, chunk_index, heading, section_path, chunk_text, embedding(vector(384))

### Indexing
- pgvector HNSW or IVFFLAT index on `chunks.embedding`
- standard indexes on `documents.doc_type`, `documents.contract_date`

## 9) Demo script (questions to show)
1. “What is the termination notice period in Contract X?”
2. “What is the governing law clause across contracts signed after Y date?”
3. “Do we allow subcontracting? What conditions apply?”
4. “Summarize payment terms for vendor agreements in 2024.”
5. “Is there an auto-renewal clause? Show the exact section.”

## 10) Known limitations + explicit "won't do in v1"
### Known limitations
- Messy PDFs can break parsing and heading detection
- RAG reduces hallucination but retrieval errors still happen if chunking is bad
- Not designed for heavy concurrency or strict latency guarantees

### Explicit "won't do in v1"
- Interacting with scanned/image-only PDFs (no OCR for now)
- Enforcing org-wide permissions / document-level ACLs
- Syncing with SharePoint / Drive / Confluence
- Multi-agent tool actions (creating tickets, approvals)
- Audit-grade compliance

## 11) v2/v3 upgrade path
### v2 Workflow enhancements
- OCR option for scanned PDFs
- Reranker (e.g., cross-encoder) for better chunk relevance
- Better document versioning and deduplication
- “List matching contracts” mode (extractive listing)

### v3 Enterprise readiness
- SSO integration + strict ACL enforcement
- Multi-source connectors
- Comprehensive audit logs + retention rules
- Evaluation harness + continuous regression tests
- Cost controls (LLM caching, tiered model routing)