CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY,
    original_text TEXT NOT NULL,
    normalized_text TEXT NOT NULL,
    subject TEXT,
    event TEXT,
    location TEXT,
    claim_date VARCHAR(100),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    domain VARCHAR(255),
    publisher VARCHAR(255),
    source_type VARCHAR(100),
    title TEXT,
    author VARCHAR(255),
    publication_date VARCHAR(100),
    discovered_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY,
    claim_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    evidence_text TEXT NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    relevance FLOAT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (claim_id) REFERENCES claims(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

CREATE TABLE IF NOT EXISTS verifications (
    id INTEGER PRIMARY KEY,
    claim_id INTEGER NOT NULL,
    verdict VARCHAR(50) NOT NULL,
    confidence VARCHAR(50) NOT NULL,
    explanation TEXT NOT NULL,
    verified_at TIMESTAMP NOT NULL,
    FOREIGN KEY (claim_id) REFERENCES claims(id)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS usage (
    id INTEGER PRIMARY KEY,
    user_identifier VARCHAR(255) NOT NULL,
    usage_date VARCHAR(10) NOT NULL,
    verification_count INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_claims_normalized_text
    ON claims(normalized_text);

CREATE INDEX IF NOT EXISTS idx_evidence_claim_id
    ON evidence(claim_id);

CREATE INDEX IF NOT EXISTS idx_evidence_source_id
    ON evidence(source_id);

CREATE INDEX IF NOT EXISTS idx_verifications_claim_id
    ON verifications(claim_id);

CREATE INDEX IF NOT EXISTS idx_usage_user_date
    ON usage(user_identifier, usage_date);
