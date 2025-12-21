-- Initialize the Get The Code database

-- Config table for storing application configuration
CREATE TABLE IF NOT EXISTS config (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SECURITY: Secret code is now managed via environment variables only.
-- The application reads from SECRET_CODE env var, not from this table.
-- Only store non-sensitive configuration here.

INSERT INTO config (key, value) VALUES ('start_date', '2025-01-01')
ON CONFLICT (key) DO NOTHING;

-- Challenge attempts log - stores all attempts where code was detected
CREATE TABLE IF NOT EXISTS challenge_attempts (
    id SERIAL PRIMARY KEY,
    user_prompt TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    referee2_decision VARCHAR(10) NOT NULL,
    referee2_reasoning TEXT,
    referee3_decision VARCHAR(10) NOT NULL,
    referee3_reasoning TEXT,
    code_leaked BOOLEAN DEFAULT FALSE,
    detection_method VARCHAR(50),  -- 'referee' or 'string_match'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- PERFORMANCE: Indexes for faster queries
-- ===========================================

-- Index for time-based queries (most common access pattern)
CREATE INDEX IF NOT EXISTS idx_challenge_attempts_created_at ON challenge_attempts(created_at DESC);

-- Index for filtering by detection method (analytics queries)
CREATE INDEX IF NOT EXISTS idx_challenge_attempts_detection ON challenge_attempts(detection_method);

-- Index for filtering by code_leaked status (security monitoring)
CREATE INDEX IF NOT EXISTS idx_challenge_attempts_leaked ON challenge_attempts(code_leaked);

-- Composite index for common query patterns (leaked attempts by time)
CREATE INDEX IF NOT EXISTS idx_challenge_attempts_leaked_time ON challenge_attempts(code_leaked, created_at DESC);

-- ===========================================
-- PERFORMANCE: PostgreSQL configuration hints
-- ===========================================
-- Note: These should be set in postgresql.conf for production:
--
-- # Connection settings
-- max_connections = 200
-- 
-- # Memory settings (adjust based on available RAM)
-- shared_buffers = 256MB
-- effective_cache_size = 768MB
-- work_mem = 4MB
-- maintenance_work_mem = 64MB
-- 
-- # Write-ahead log settings
-- wal_buffers = 16MB
-- checkpoint_completion_target = 0.9
-- 
-- # Query planner settings
-- random_page_cost = 1.1
-- effective_io_concurrency = 200

