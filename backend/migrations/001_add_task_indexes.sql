-- Migration: Add indexes to tasks table for performance optimization
-- Task: T130
-- Date: 2025-12-12
--
-- This migration adds two indexes to the tasks table:
-- 1. idx_tasks_user_id - Improves query performance when filtering tasks by user
-- 2. idx_tasks_completed - Improves query performance when filtering by completion status
--
-- These indexes are particularly useful for:
-- - GET /api/{user_id}/tasks (filters by user_id)
-- - GET /api/{user_id}/tasks?status=pending (filters by user_id and completed)
-- - GET /api/{user_id}/tasks?status=completed (filters by user_id and completed)

-- Add index on user_id if it doesn't exist
-- Note: SQLModel may have already created this index via index=True
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);

-- Add index on completed status
-- This is the new index being added in this migration
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);

-- Verify indexes were created
-- Run this query to check:
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'tasks';
