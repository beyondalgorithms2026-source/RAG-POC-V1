# RAG-POC-V1

## Objective
The objective of this project is to implement a Basic Retrieval-Augmented Generation (RAG) workflow PoC (Proof of Concept). This PoC demonstrates how to build and evaluate a robust vector search foundation, embedding generation, and retrieval pipelines, independent of LLM generative layers—ensuring retrieval accuracy can be measured, debugged, and optimized systematically. 

It provides an end-to-end foundation featuring:
* A backend built with FastAPI.
* A vector database using pgvector.
* Integrated evaluation tools to assess retrieval performance.
* A basic frontend interface to interact with the system.

## Project Structure
The core application code is located in the `rag-poc-v1/` directory. All initial setup commands should be run from within that directory.

## Quickstart Guide

### 0) Navigate to Project Directory
```bash
cd rag-poc-v1
```

### 1) Start Database container
This will start PostgreSQL with the `pgvector` extension.
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
*(Note: update the `.env` file with your specific API keys or configuration if necessary).*

### 3) Run migrations
Sets up the necessary tables for embeddings and documents.
```bash
python -m app.db.migrate
```

### 4) Verify Database Schema
```bash
python -m app.db.verify_db
```

### 5) Start Backend Server
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`. 

### 6) Run Tests
```bash
pytest
```

---

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
