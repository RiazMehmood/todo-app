-- Migration: Add time_entries table for time tracking
-- Specification: specs/005-cloud-native-deployment/data-model.md
-- Created: 2025-12-24
-- Purpose: Enable time tracking for tasks with start/stop functionality

-- UP Migration
CREATE TABLE IF NOT EXISTS time_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id INTEGER NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ended_at TIMESTAMP WITH TIME ZONE,
    elapsed_seconds INTEGER,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT time_entries_positive_elapsed CHECK (elapsed_seconds IS NULL OR elapsed_seconds >= 0),
    CONSTRAINT time_entries_valid_time_range CHECK (ended_at IS NULL OR ended_at >= started_at)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_time_entries_task_id ON time_entries(task_id);
CREATE INDEX IF NOT EXISTS idx_time_entries_user_id ON time_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_time_entries_started_at ON time_entries(started_at);

-- Create trigger function to auto-calculate elapsed_seconds
CREATE OR REPLACE FUNCTION calculate_time_entry_elapsed() RETURNS TRIGGER AS $$
BEGIN
  -- Calculate elapsed_seconds only if ended_at is set
  IF NEW.ended_at IS NOT NULL THEN
    NEW.elapsed_seconds := EXTRACT(EPOCH FROM (NEW.ended_at - NEW.started_at))::INTEGER;
  ELSE
    NEW.elapsed_seconds := NULL;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS time_entries_calculate_elapsed_trigger ON time_entries;
CREATE TRIGGER time_entries_calculate_elapsed_trigger
BEFORE INSERT OR UPDATE ON time_entries
FOR EACH ROW EXECUTE FUNCTION calculate_time_entry_elapsed();

-- Add comments for documentation
COMMENT ON TABLE time_entries IS 'Stores time tracking entries for tasks';
COMMENT ON COLUMN time_entries.elapsed_seconds IS 'Auto-calculated from ended_at - started_at when timer stops';
COMMENT ON COLUMN time_entries.started_at IS 'When timer was started';
COMMENT ON COLUMN time_entries.ended_at IS 'When timer was stopped (NULL if still running)';

-- DOWN Migration (rollback)
-- To rollback this migration, run these commands:
-- DROP TRIGGER IF EXISTS time_entries_calculate_elapsed_trigger ON time_entries;
-- DROP FUNCTION IF EXISTS calculate_time_entry_elapsed();
-- DROP TABLE IF EXISTS time_entries CASCADE;
