-- Migration: Add indexes for analytics queries
-- Task: T099 (Phase 7 - Performance Optimization)
-- Created: 2025-12-25
-- Purpose: Optimize analytics queries by adding indexes on date and completion columns
-- Note: Adjusted to match actual tasks table schema (completed instead of status)

-- UP Migration
-- Add index on created_at for date range queries in analytics
-- Used by: calculate_metrics(), get_completion_trend(), get_tasks_by_*()
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

-- Add index on completed for completion tracking
-- Used by: calculate_metrics(), filter by completion status
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);

-- Add index on updated_at for completion trend queries
-- Used by: get_completion_trend() when filtering completed tasks
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at);

-- Add composite index for common analytics query pattern (user_id + created_at)
-- Improves performance for date range filtered queries per user
CREATE INDEX IF NOT EXISTS idx_tasks_user_created ON tasks(user_id, created_at);

-- Add composite index for completion filtering per user
-- Improves performance for completion status queries
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed ON tasks(user_id, completed);

-- Add index on search_vector for full-text search
-- Used by: search queries
CREATE INDEX IF NOT EXISTS idx_tasks_search_vector ON tasks USING gin(search_vector);

-- Analyze tables to update query planner statistics
ANALYZE tasks;
ANALYZE time_entries;

-- Verify indexes were created
-- Run this query to check:
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'tasks' ORDER BY indexname;

-- DOWN Migration (rollback)
-- To rollback this migration, run these commands:
-- DROP INDEX IF EXISTS idx_tasks_created_at;
-- DROP INDEX IF EXISTS idx_tasks_completed;
-- DROP INDEX IF EXISTS idx_tasks_updated_at;
-- DROP INDEX IF EXISTS idx_tasks_user_created;
-- DROP INDEX IF EXISTS idx_tasks_user_completed;
-- DROP INDEX IF EXISTS idx_tasks_search_vector;
