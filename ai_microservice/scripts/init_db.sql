CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS properties;

CREATE TABLE IF NOT EXISTS properties (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    price FLOAT,
    min_investment FLOAT,
    investment_period INTEGER,
    risk_assessment VARCHAR,
    rental_yield FLOAT,
    expected_roi FLOAT,
    location VARCHAR,
    property_type VARCHAR,
    embedding VECTOR(384)
);


