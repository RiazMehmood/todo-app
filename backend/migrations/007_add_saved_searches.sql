-- Migration: Add saved_searches table for storing user search queries
-- Specification: specs/005-cloud-native-deployment/data-model.md
-- Created: 2025-12-24
-- Purpose: Enable users to save and reuse complex search queries

-- UP Migration
CREATE TABLE IF NOT EXISTS saved_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    query_params JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT saved_searches_name_not_empty CHECK (length(trim(name)) > 0),
    CONSTRAINT saved_searches_user_name_unique UNIQUE (user_id, name)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_saved_searches_user_id ON saved_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_searches_query_params ON saved_searches USING GIN(query_params);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_saved_searches_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS saved_searches_updated_at_trigger ON saved_searches;
CREATE TRIGGER saved_searches_updated_at_trigger
BEFORE UPDATE ON saved_searches
FOR EACH ROW EXECUTE FUNCTION update_saved_searches_updated_at();

-- Add comment for documentation
COMMENT ON TABLE saved_searches IS 'Stores user-defined search queries for quick access';
COMMENT ON COLUMN saved_searches.query_params IS 'JSON object containing search filters (status, priority, tags, date ranges)';

-- DOWN Migration (rollback)
-- To rollback this migration, run these commands:
-- DROP TRIGGER IF EXISTS saved_searches_updated_at_trigger ON saved_searches;
-- DROP FUNCTION IF EXISTS update_saved_searches_updated_at();
-- DROP TABLE IF EXISTS saved_searches CASCADE;
