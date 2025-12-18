-- Migration: Add AI Chatbot Integration Tables
-- Feature: 003-ai-chatbot-integration
-- Date: 2025-12-16
-- Description: Creates tables for user AI preferences, conversations, and messages

-- ============================================================================
-- 1. UserPreferences Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ai_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    ai_opt_in_date TIMESTAMP,
    preferred_language VARCHAR(10) DEFAULT 'en' NOT NULL,
    privacy_consent_version VARCHAR(10),
    auto_detect_language BOOLEAN DEFAULT TRUE NOT NULL,
    voice_input_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT check_ai_consent CHECK (
        (ai_enabled = FALSE) OR
        (ai_enabled = TRUE AND privacy_consent_version IS NOT NULL AND ai_opt_in_date IS NOT NULL)
    ),
    CONSTRAINT check_language CHECK (preferred_language IN ('en', 'ur'))
);

-- ============================================================================
-- 2. Conversation Table (Hackathon Requirement - Page 18)
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- ============================================================================
-- 3. Message Table (Hackathon Requirement - Page 18, Enhanced)
-- ============================================================================

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- Enhanced attributes (our extensions)
    language VARCHAR(10) CHECK (language IN ('en', 'ur')),
    related_task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    intent_detected VARCHAR(50),
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    extra_data JSONB,
    CONSTRAINT check_message_length CHECK (LENGTH(content) > 0 AND LENGTH(content) <= 2000)
);

-- ============================================================================
-- 4. Enhance Tasks Table with AI Metadata
-- ============================================================================

ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS created_via_ai BOOLEAN DEFAULT FALSE NOT NULL,
    ADD COLUMN IF NOT EXISTS ai_suggested_priority INTEGER CHECK (ai_suggested_priority >= 1 AND ai_suggested_priority <= 5),
    ADD COLUMN IF NOT EXISTS original_nl_input TEXT;

-- ============================================================================
-- 5. Create Indexes for Performance
-- ============================================================================

-- UserPreferences indexes
CREATE INDEX IF NOT EXISTS idx_user_prefs_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_prefs_ai_enabled ON user_preferences(ai_enabled);

-- Conversations indexes
CREATE INDEX IF NOT EXISTS idx_conversation_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_updated_at ON conversations(updated_at DESC);

-- Messages indexes
CREATE INDEX IF NOT EXISTS idx_message_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_message_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_message_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_message_related_task ON messages(related_task_id);
CREATE INDEX IF NOT EXISTS idx_message_conversation_created ON messages(conversation_id, created_at DESC);

-- Tasks AI indexes
CREATE INDEX IF NOT EXISTS idx_tasks_created_via_ai ON tasks(created_via_ai);

-- ============================================================================
-- 6. Comments
-- ============================================================================

COMMENT ON TABLE user_preferences IS 'Stores user AI feature preferences and privacy consent';
COMMENT ON TABLE conversations IS 'Chat conversation sessions between user and AI (Hackathon Page 18)';
COMMENT ON TABLE messages IS 'Individual messages within conversations (Hackathon Page 18)';
COMMENT ON COLUMN tasks.created_via_ai IS 'Indicates task was created through AI chat';
COMMENT ON COLUMN tasks.ai_suggested_priority IS 'AI-suggested priority level (1-5)';
COMMENT ON COLUMN tasks.original_nl_input IS 'Original natural language input that created the task';

-- ============================================================================
-- Migration Complete
-- ============================================================================
