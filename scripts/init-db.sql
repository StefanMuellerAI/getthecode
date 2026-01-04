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
-- STATS: Conversations and Messages tables
-- ===========================================

-- Conversations table - tracks each chat session
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(50) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    has_code_leak BOOLEAN DEFAULT FALSE
);

-- Messages table - stores all messages with referee decisions
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(50) REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    sanitized_content TEXT, -- For user messages (sanitized version)
    referee2_decision VARCHAR(10), -- 'PASS' or 'STOP'
    referee2_reasoning TEXT,
    referee3_decision VARCHAR(10),
    referee3_reasoning TEXT,
    code_detected BOOLEAN DEFAULT FALSE,
    detection_method VARCHAR(50), -- 'referee', 'string_match_winner', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for messages table
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_code_detected ON messages(code_detected);

-- Indexes for conversations table
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_has_code_leak ON conversations(has_code_leak);

-- ===========================================
-- GIFT CODE REDEMPTION SYSTEM
-- ===========================================

-- Game status table (single row for current game state)
CREATE TABLE IF NOT EXISTS game_status (
    id INTEGER PRIMARY KEY DEFAULT 1,
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, won, pending_claim, redeemed
    last_winner_conversation_id VARCHAR(50),
    last_win_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT single_row CHECK (id = 1)
);

-- Initialize game status
INSERT INTO game_status (id, status) VALUES (1, 'active')
ON CONFLICT (id) DO NOTHING;

-- Gift codes table - stores Amazon gift codes
-- SECURITY: code field uses TEXT to accommodate encrypted values
CREATE TABLE IF NOT EXISTS gift_codes (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL,
    value INTEGER NOT NULL DEFAULT 100,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    burned_at TIMESTAMP,
    winner_conversation_id VARCHAR(50),
    winner_redemption_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_gift_codes_available ON gift_codes(burned_at) WHERE burned_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_gift_codes_burned ON gift_codes(burned_at) WHERE burned_at IS NOT NULL;

-- Redemptions table - secure one-time redemption tokens
CREATE TABLE IF NOT EXISTS redemptions (
    id SERIAL PRIMARY KEY,
    token VARCHAR(128) UNIQUE NOT NULL,
    conversation_id VARCHAR(50) NOT NULL,
    detection_method VARCHAR(50) NOT NULL,  -- 'automatic' or 'manual_claim'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    codes_value INTEGER DEFAULT 0,  -- Total value of codes at time of win
    
    -- For manual claims
    claim_id INTEGER,
    admin_notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_redemptions_token ON redemptions(token);
CREATE INDEX IF NOT EXISTS idx_redemptions_conversation ON redemptions(conversation_id);
CREATE INDEX IF NOT EXISTS idx_redemptions_expires ON redemptions(expires_at);

-- Winner claims table - for gradual extraction claims
-- NOTE: email field replaces linkedin_profile (Double Opt-In verification required)
-- SECURITY: claimed_code and claim_message use TEXT to accommodate encrypted values
CREATE TABLE IF NOT EXISTS winner_claims (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(50) NOT NULL,
    claimed_code TEXT NOT NULL,
    email VARCHAR(255) NOT NULL,
    claim_message TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    reviewed_at TIMESTAMP,
    reviewed_by VARCHAR(100),
    review_notes TEXT,
    redemption_id INTEGER REFERENCES redemptions(id)
);

CREATE INDEX IF NOT EXISTS idx_claims_status ON winner_claims(status);
CREATE INDEX IF NOT EXISTS idx_claims_conversation ON winner_claims(conversation_id);
CREATE INDEX IF NOT EXISTS idx_claims_created ON winner_claims(created_at DESC);

-- ===========================================
-- EMAIL VERIFICATION SYSTEM (Double Opt-In)
-- ===========================================

-- Email verification codes for claim submissions
-- SECURITY: code field uses TEXT to accommodate encrypted values
CREATE TABLE IF NOT EXISTS email_verifications (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    code TEXT NOT NULL,
    conversation_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP,
    ip_address VARCHAR(45)
);

CREATE INDEX IF NOT EXISTS idx_email_verifications_email ON email_verifications(email, conversation_id);
CREATE INDEX IF NOT EXISTS idx_email_verifications_expires ON email_verifications(expires_at);
CREATE INDEX IF NOT EXISTS idx_email_verifications_ip ON email_verifications(ip_address, created_at DESC);

-- Redemption attempts log (for security monitoring)
CREATE TABLE IF NOT EXISTS redemption_attempts (
    id SERIAL PRIMARY KEY,
    token_attempted VARCHAR(128),
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN DEFAULT FALSE,
    failure_reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_redemption_attempts_ip ON redemption_attempts(ip_address, created_at DESC);

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

