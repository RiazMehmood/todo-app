# Data Model: AI Chatbot Integration

**Feature**: 003-ai-chatbot-integration
**Date**: 2025-12-16
**Status**: Design

## Overview

This document defines the data model extensions needed for AI chatbot functionality. It builds upon the existing Phase II data model (User, Task) and adds new entities for chat functionality.

## Entity Relationship Diagram

```
User (existing)
  ├── 1:N → Task (existing, enhanced)
  ├── 1:1 → UserPreferences (new)
  └── 1:N → Conversation (new)
        └── 1:N → Message (new)

AIAgent (new, managed by Agents SDK)
  └── 1:1 → User
```

## Entities

### 1. User (Existing - No Changes)

Existing entity from Phase II. No schema changes required.

**Attributes**:
- `id`: UUID (Primary Key)
- `email`: String (Unique)
- `name`: String
- `password_hash`: String
- `created_at`: DateTime
- `updated_at`: DateTime

---

### 2. Task (Existing - Enhanced)

Existing entity with new optional AI-related metadata fields.

**New Attributes**:
- `created_via_ai`: Boolean (default: False) - Indicates task was created through AI chat
- `ai_suggested_priority`: Integer (nullable) - Priority suggested by AI (1-5 scale)
- `original_nl_input`: Text (nullable) - Original natural language input that created the task

**Existing Attributes** (unchanged):
- `id`: Integer (Primary Key, Auto-increment)
- `user_id`: UUID (Foreign Key → User.id)
- `title`: String(200) (Required)
- `description`: Text (Optional)
- `completed`: Boolean (default: False)
- `created_at`: DateTime
- `updated_at`: DateTime

**Indexes**:
- Existing: `idx_tasks_user_id` on `user_id`
- Existing: `idx_tasks_completed` on `completed`
- New: `idx_tasks_created_via_ai` on `created_via_ai` (for analytics)

**Validation Rules**:
- `title`: 1-200 characters, non-empty
- `description`: max 1000 characters (optional)
- `ai_suggested_priority`: 1-5 if provided
- All existing validation rules remain

---

### 3. UserPreferences (New)

Stores user preferences for AI features and settings.

**Attributes**:
- `id`: Integer (Primary Key, Auto-increment)
- `user_id`: UUID (Foreign Key → User.id, Unique)
- `ai_enabled`: Boolean (default: False) - User has opted in to AI features
- `ai_opt_in_date`: DateTime (nullable) - When user enabled AI
- `preferred_language`: String(10) (default: 'en') - Preferred language ('en' or 'ur')
- `privacy_consent_version`: String(10) - Version of privacy policy user consented to
- `auto_detect_language`: Boolean (default: True) - Auto-detect language from input
- `voice_input_enabled`: Boolean (default: False) - Voice input feature toggle
- `created_at`: DateTime
- `updated_at`: DateTime

**Indexes**:
- `idx_user_prefs_user_id` on `user_id` (Unique)
- `idx_user_prefs_ai_enabled` on `ai_enabled` (for counting active AI users)

**Validation Rules**:
- `user_id`: Must exist in User table
- `preferred_language`: Must be 'en' or 'ur'
- `privacy_consent_version`: Required if `ai_enabled` is True
- One preferences record per user (enforced by unique constraint)

**Constraints**:
- UNIQUE constraint on `user_id`
- CHECK: `ai_enabled` = True requires `privacy_consent_version` IS NOT NULL
- CHECK: `ai_opt_in_date` IS NOT NULL if `ai_enabled` = True

---

### 4. Conversation (New)

Represents a chat conversation session between user and AI assistant.

**Per Hackathon Specification** (Page 18): Required table with exact schema.

**Attributes**:
- `id`: Integer (Primary Key, Auto-increment)
- `user_id`: UUID (Foreign Key → User.id, Required)
- `created_at`: DateTime (Required)
- `updated_at`: DateTime (Required)

**Indexes**:
- `idx_conversation_user_id` on `user_id` - For querying user's conversations
- `idx_conversation_updated_at` on `updated_at` DESC - For recent conversations

**Validation Rules**:
- `user_id`: Must exist in User table
- One active conversation per user (enforced at application level)

**Cascade Rules**:
- ON DELETE User → CASCADE delete all Conversations

**Purpose**:
- Groups related messages into conversation sessions
- Tracks when conversation started and last message time
- Required by Hackathon II Phase III specification

---

### 5. Message (New)

Stores individual chat messages within conversations.

**Per Hackathon Specification** (Page 18): Required table with core attributes, enhanced with AI metadata.

**Core Attributes** (Hackathon Required):
- `id`: Integer (Primary Key, Auto-increment)
- `user_id`: UUID (Foreign Key → User.id, Required)
- `conversation_id`: Integer (Foreign Key → Conversation.id, Required)
- `role`: Enum('user', 'assistant') (Required) - Who sent the message
- `content`: Text (Required) - The message content
- `created_at`: DateTime (Required)

**Enhanced Attributes** (Our Extensions):
- `language`: String(10) (nullable) - Language of the message ('en' or 'ur')
- `related_task_id`: Integer (Foreign Key → Task.id, nullable) - Task related to this message
- `intent_detected`: String(50) (nullable) - AI-detected intent (create_task, query_tasks, etc.)
- `confidence_score`: Float (nullable) - AI confidence in interpretation (0.0-1.0)
- `metadata`: JSON (nullable) - Additional context (e.g., {"command": "create", "entities": ["milk"]})

**Indexes**:
- `idx_message_conversation_id` on `conversation_id` - For querying conversation messages
- `idx_message_user_id` on `user_id` - For querying user's messages
- `idx_message_created_at` on `created_at` DESC - For chronological ordering
- `idx_message_related_task` on `related_task_id` - For finding messages about specific tasks
- Composite: `idx_message_conversation_created` on (`conversation_id`, `created_at` DESC) - Optimized conversation queries

**Validation Rules**:
- `content`: Non-empty, max 2000 characters
- `role`: Must be 'user' or 'assistant'
- `language`: Must be 'en' or 'ur' if provided
- `confidence_score`: 0.0 to 1.0 if provided
- `intent_detected`: Predefined set of intents (create_task, query_tasks, update_task, delete_task, help, etc.)
- `conversation_id`: Must reference existing conversation

**State Transitions**:
N/A - Messages are immutable once created (no updates, only soft delete for privacy)

**Cascade Rules**:
- ON DELETE User → CASCADE delete all Messages
- ON DELETE Conversation → CASCADE delete all Messages
- ON DELETE Task → SET NULL on related_task_id (preserve chat history even if task deleted)

---

### 6. AIAgent (Conceptual - Managed by Agents SDK)

This entity is NOT stored in our database but managed by the Agents SDK runtime. Documented here for completeness.

**Runtime Attributes** (in Agents SDK):
- `agent_id`: String (Unique identifier)
- `user_id`: UUID (Which user this agent serves)
- `context`: Object (Conversation history and state)
- `model_version`: String (OpenAI model being used, e.g., "gpt-4")
- `session_id`: String (Current chat session)
- `last_active`: DateTime

**Lifecycle**:
- Created when user sends first message after opt-in
- Maintained in memory/cache during active session
- Persisted to Agents SDK storage between sessions
- Destroyed when user opts out of AI

**Context Management**:
- Recent conversation history (last N messages)
- User's task summary (task count, recent tasks)
- User preferences (language, etc.)
- Session metadata

---

## Data Flow

### User Opt-In Flow
1. User → UserPreferences.ai_enabled = True
2. System creates privacy_consent_version record
3. System sets ai_opt_in_date
4. AI chat interface becomes available

### Chat Message Flow
1. User sends first message → System creates or retrieves Conversation
2. User sends message → Message (role='user', conversation_id)
3. AI processes message via MCP/Agents SDK
4. AI detects intent → Message.intent_detected
5. AI performs action (e.g., creates Task with created_via_ai=True)
6. AI responds → Message (role='assistant', conversation_id, related_task_id if applicable)
7. Conversation.updated_at timestamp updated

### Task Creation via AI
1. User Message created with intent_detected='create_task'
2. Task created with:
   - created_via_ai = True
   - original_nl_input = user's message content
   - ai_suggested_priority (optional)
3. AI Message created with related_task_id = new Task.id
4. Confirmation message sent to user

---

## Migration Strategy

### Phase 1: Add New Tables
```sql
-- UserPreferences table
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
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

-- Conversation table (Hackathon Requirement - Page 18)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Message table (Hackathon Requirement - Page 18, Enhanced)
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- Enhanced attributes (our extensions)
    language VARCHAR(10) CHECK (language IN ('en', 'ur')),
    related_task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    intent_detected VARCHAR(50),
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    metadata JSONB,
    CONSTRAINT check_message_length CHECK (LENGTH(content) > 0 AND LENGTH(content) <= 2000)
);

-- Indexes for UserPreferences
CREATE INDEX idx_user_prefs_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_prefs_ai_enabled ON user_preferences(ai_enabled);

-- Indexes for Conversations
CREATE INDEX idx_conversation_user_id ON conversations(user_id);
CREATE INDEX idx_conversation_updated_at ON conversations(updated_at DESC);

-- Indexes for Messages
CREATE INDEX idx_message_conversation_id ON messages(conversation_id);
CREATE INDEX idx_message_user_id ON messages(user_id);
CREATE INDEX idx_message_created_at ON messages(created_at DESC);
CREATE INDEX idx_message_related_task ON messages(related_task_id);
CREATE INDEX idx_message_conversation_created ON messages(conversation_id, created_at DESC);
```

### Phase 2: Enhance Tasks Table
```sql
-- Add AI-related columns to existing tasks table
ALTER TABLE tasks
    ADD COLUMN created_via_ai BOOLEAN DEFAULT FALSE NOT NULL,
    ADD COLUMN ai_suggested_priority INTEGER CHECK (ai_suggested_priority >= 1 AND ai_suggested_priority <= 5),
    ADD COLUMN original_nl_input TEXT;

-- Add index
CREATE INDEX idx_tasks_created_via_ai ON tasks(created_via_ai);
```

### Rollback Plan
```sql
-- Remove AI columns from tasks
ALTER TABLE tasks
    DROP COLUMN created_via_ai,
    DROP COLUMN ai_suggested_priority,
    DROP COLUMN original_nl_input;

-- Drop messages table (must be before conversations due to FK)
DROP TABLE messages;

-- Drop conversations table
DROP TABLE conversations;

-- Drop user preferences table
DROP TABLE user_preferences;
```

---

## Privacy & Data Retention

### Chat History Retention
- **Default**: Retain indefinitely for user convenience
- **User Control**: Users can delete all chat history via settings
- **Opt-Out**: Disabling AI features optionally deletes all Conversations and Messages

### Personal Data
- Messages may contain sensitive task information
- Must be encrypted at rest (PostgreSQL encryption)
- Must be encrypted in transit to OpenAI (HTTPS)
- Subject to user's right to deletion (GDPR Article 17)

### Data Deletion
When user opts out of AI:
1. Optionally delete all Conversations and Messages for that user
2. Set UserPreferences.ai_enabled = False
3. Preserve UserPreferences record for audit trail
4. Mark deleted messages with deleted_at timestamp (soft delete)

---

## Performance Considerations

### Query Optimization
- Composite index on (user_id, timestamp DESC) for fast chat history retrieval
- Limit chat history queries to last 100 messages by default
- Use pagination for loading older messages

### Storage Estimates
- Average Message: ~500 bytes (text + metadata)
- Average Conversation: ~50 bytes
- 100 messages per user: ~50 KB
- 1000 active users: ~50 MB total messages + ~50 KB conversations
- PostgreSQL JSONB for efficient metadata storage

### Scaling
- Messages can grow large over time
- Consider archiving messages older than 6 months
- Partition table by conversation_id or user_id if needed (future optimization)

---

## Analytics & Metrics

Queries enabled by this data model:

1. **AI Adoption Rate**:
   ```sql
   SELECT COUNT(*) FILTER (WHERE ai_enabled) * 100.0 / COUNT(*)
   FROM user_preferences;
   ```

2. **AI vs Manual Task Creation**:
   ```sql
   SELECT created_via_ai, COUNT(*)
   FROM tasks
   GROUP BY created_via_ai;
   ```

3. **Average Confidence Score**:
   ```sql
   SELECT AVG(confidence_score)
   FROM messages
   WHERE role = 'assistant' AND confidence_score IS NOT NULL;
   ```

4. **Intent Distribution**:
   ```sql
   SELECT intent_detected, COUNT(*)
   FROM messages
   WHERE role = 'user'
   GROUP BY intent_detected
   ORDER BY COUNT(*) DESC;
   ```

5. **Active Conversations**:
   ```sql
   SELECT COUNT(*) as active_conversations
   FROM conversations
   WHERE updated_at > NOW() - INTERVAL '24 hours';
   ```

---

## Summary

**New Tables**: 3 (UserPreferences, Conversation, Message)
**Enhanced Tables**: 1 (Task with 3 new optional columns)
**Total Indexes**: 11 new indexes
**Constraints**: 6 validation checks
**Foreign Keys**: 5 relationships

This data model fully complies with Hackathon II Phase III requirements (Page 18: Task, Conversation, Message tables) while supporting all user stories and maintaining clean separation from existing Phase II functionality.

**Hackathon Compliance**:
- ✅ Task table: Enhanced with AI metadata (created_via_ai, ai_suggested_priority, original_nl_input)
- ✅ Conversation table: Required schema (id, user_id, created_at, updated_at)
- ✅ Message table: Required core schema (id, user_id, conversation_id, role, content, created_at) + optional enhancements
