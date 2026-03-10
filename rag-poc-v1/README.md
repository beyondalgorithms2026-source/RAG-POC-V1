# RAG PoC v1

## Quickstart

### 1) Start Database container
```bash
docker compose up -d
```

### 2) Create virtual environment & install dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3) Run migrations
```bash
python -m app.db.migrate
```

### 4) Verify Database Schema
```bash
python -m app.db.verify_db
```

### 5) Start backend
```bash
uvicorn app.main:app --reload
```

### 6) Run tests
```bash
pytest
```

## M8 Retrieval Evaluation

To run the standalone retrieval evaluation harness (which validates vector search accuracy without any LLM overhead):

1. **Activate Environment**
   ```bash
   cd backend
   source venv/bin/activate
   ```
2. **Run Harness Options**
   ```bash
   # Standard full run
   python -m app.eval.retrieval_eval --k 6

   # Debug run with compact response tables (limited to 5 questions)
   python -m app.eval.retrieval_eval --k 6 --debug --limit 5

   # Debug a single ad-hoc question
   python -m app.eval.retrieval_eval --debug-question "What is Confidential Information?" --k 6
   ```

A detailed JSON report highlighting failures and pass rates will be saved to `eval_report.json` in the project root.
