CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    min_investment FLOAT,
    lock_in_years INTEGER,
    risk_rating VARCHAR,
    embedding VECTOR(384)
);

CREATE INDEX IF NOT EXISTS idx_properties_embedding
    ON properties
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
