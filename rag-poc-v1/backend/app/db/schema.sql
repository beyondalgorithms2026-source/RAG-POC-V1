CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    file_path TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    doc_type TEXT,
    contract_date DATE,
    hash_sha256 TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    heading TEXT,
    section_path TEXT,
    chunk_text TEXT NOT NULL,
    token_count INT,
    embedding vector(384),
    search_tsv tsvector,
    created_at TIMESTAMPTZ DEFAULT now()
);
