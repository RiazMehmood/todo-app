-- Migration: Add full-text search vector to tasks table
-- Specification: specs/005-cloud-native-deployment/data-model.md
-- Created: 2025-12-24
-- Purpose: Enable PostgreSQL full-text search with ts_vector and GIN index for advanced search

-- UP Migration
-- Add search_vector column to tasks table
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Create GIN index for full-text search (significantly improves search performance)
CREATE INDEX IF NOT EXISTS idx_tasks_search_vector ON tasks USING GIN(search_vector);

-- Create trigger function to auto-update search_vector on insert/update
CREATE OR REPLACE FUNCTION tasks_search_vector_update() RETURNS TRIGGER AS $$
BEGIN
  -- Weight: 'A' for title (highest priority), 'B' for description (lower priority)
  NEW.search_vector :=
    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update search_vector before insert or update
DROP TRIGGER IF EXISTS tasks_search_vector_trigger ON tasks;
CREATE TRIGGER tasks_search_vector_trigger
BEFORE INSERT OR UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION tasks_search_vector_update();

-- Backfill existing tasks with search_vector data
UPDATE tasks SET search_vector =
  setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
  setweight(to_tsvector('english', COALESCE(description, '')), 'B')
WHERE search_vector IS NULL;

-- DOWN Migration (rollback)
-- To rollback this migration, run these commands:
-- DROP TRIGGER IF EXISTS tasks_search_vector_trigger ON tasks;
-- DROP FUNCTION IF EXISTS tasks_search_vector_update();
-- DROP INDEX IF EXISTS idx_tasks_search_vector;
-- ALTER TABLE tasks DROP COLUMN IF EXISTS search_vector;
