-- Migration: Add task_templates table for storing reusable task templates
-- Specification: specs/005-cloud-native-deployment/data-model.md
-- Created: 2025-12-24
-- Purpose: Enable users to create and instantiate task templates with placeholders

-- UP Migration
CREATE TABLE IF NOT EXISTS task_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    tasks_definition JSONB NOT NULL,
    placeholders JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT task_templates_name_not_empty CHECK (length(trim(name)) > 0),
    CONSTRAINT task_templates_user_name_unique UNIQUE (user_id, name),
    CONSTRAINT task_templates_max_tasks CHECK (jsonb_array_length(tasks_definition) <= 50),
    CONSTRAINT task_templates_max_placeholders CHECK (jsonb_array_length(placeholders) <= 10)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_task_templates_user_id ON task_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_task_templates_tasks_definition ON task_templates USING GIN(tasks_definition);
CREATE INDEX IF NOT EXISTS idx_task_templates_placeholders ON task_templates USING GIN(placeholders);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_task_templates_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS task_templates_updated_at_trigger ON task_templates;
CREATE TRIGGER task_templates_updated_at_trigger
BEFORE UPDATE ON task_templates
FOR EACH ROW EXECUTE FUNCTION update_task_templates_updated_at();

-- Add comments for documentation
COMMENT ON TABLE task_templates IS 'Stores reusable task templates with placeholder support';
COMMENT ON COLUMN task_templates.tasks_definition IS 'JSON array of task objects with placeholders like {{PROJECT_NAME}}';
COMMENT ON COLUMN task_templates.placeholders IS 'JSON array of required placeholder variable names';

-- DOWN Migration (rollback)
-- To rollback this migration, run these commands:
-- DROP TRIGGER IF EXISTS task_templates_updated_at_trigger ON task_templates;
-- DROP FUNCTION IF EXISTS update_task_templates_updated_at();
-- DROP TABLE IF EXISTS task_templates CASCADE;
