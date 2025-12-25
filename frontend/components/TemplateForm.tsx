'use client';

/**
 * TemplateForm Component
 *
 * Implements: User Story 2 (Task Templates) from intermediate-advanced-features.md
 * Contract: specs/005-cloud-native-deployment/contracts/templates-api.yaml
 *
 * Form for creating and editing task templates with:
 * - Dynamic task addition/removal
 * - Placeholder detection and validation (max 10)
 * - Task limit validation (max 50)
 * - Real-time {{PLACEHOLDER}} syntax highlighting
 * - Full TypeScript type safety
 */

import { useState, useEffect } from 'react';
import { PlusIcon, TrashIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

// === Type Definitions from API Contract ===

interface TaskDefinition {
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  tags?: string[];
  due_date_offset?: number;
}

interface TemplateFormData {
  name: string;
  description?: string;
  tasks_definition: TaskDefinition[];
}

interface TemplateFormProps {
  /** User ID for API calls */
  userId: string;
  /** Initial data for editing existing template */
  initialData?: TemplateFormData & { id?: string };
  /** Submit handler receives validated template data */
  onSubmit: (templateData: TemplateFormData) => Promise<void>;
  /** Cancel handler */
  onCancel: () => void;
}

// === Constants from Specification ===
const MAX_PLACEHOLDERS = 10; // Spec: max 10 placeholders per template
const MAX_TASKS = 50; // Spec: max 50 tasks per template
const PLACEHOLDER_PATTERN = /\{\{([A-Z_][A-Z0-9_]*)\}\}/g; // Spec: {{VARIABLE_NAME}} syntax

export function TemplateForm({
  userId,
  initialData,
  onSubmit,
  onCancel
}: TemplateFormProps) {
  // === Form State ===
  const [name, setName] = useState(initialData?.name || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [tasks, setTasks] = useState<TaskDefinition[]>(
    initialData?.tasks_definition || [
      {
        title: '',
        description: '',
        priority: 'medium',
        tags: [],
        due_date_offset: 0
      }
    ]
  );

  // === Validation State ===
  const [detectedPlaceholders, setDetectedPlaceholders] = useState<string[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // === Placeholder Detection (Auto-detect from all fields) ===
  useEffect(() => {
    const allPlaceholders = new Set<string>();

    // Scan all tasks for placeholders
    tasks.forEach((task) => {
      // Scan title
      if (task.title) {
        const matches = task.title.matchAll(PLACEHOLDER_PATTERN);
        for (const match of matches) {
          allPlaceholders.add(match[1]);
        }
      }

      // Scan description
      if (task.description) {
        const matches = task.description.matchAll(PLACEHOLDER_PATTERN);
        for (const match of matches) {
          allPlaceholders.add(match[1]);
        }
      }

      // Scan tags
      if (task.tags) {
        task.tags.forEach((tag) => {
          const matches = tag.matchAll(PLACEHOLDER_PATTERN);
          for (const match of matches) {
            allPlaceholders.add(match[1]);
          }
        });
      }
    });

    setDetectedPlaceholders(Array.from(allPlaceholders).sort());
  }, [tasks]);

  // === Validation ===
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Validate template name
    if (!name.trim()) {
      newErrors.name = 'Template name is required';
    } else if (name.length > 100) {
      newErrors.name = 'Template name must be 100 characters or less';
    }

    // Validate task count
    if (tasks.length === 0) {
      newErrors.tasks = 'Template must contain at least one task';
    } else if (tasks.length > MAX_TASKS) {
      newErrors.tasks = `Template cannot exceed ${MAX_TASKS} tasks`;
    }

    // Validate placeholder count
    if (detectedPlaceholders.length > MAX_PLACEHOLDERS) {
      newErrors.placeholders = `Template cannot exceed ${MAX_PLACEHOLDERS} placeholders (found ${detectedPlaceholders.length})`;
    }

    // Validate each task
    tasks.forEach((task, index) => {
      if (!task.title.trim()) {
        newErrors[`task_${index}_title`] = `Task ${index + 1} must have a title`;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // === Task Management ===
  const addTask = () => {
    if (tasks.length >= MAX_TASKS) {
      setErrors({ tasks: `Maximum ${MAX_TASKS} tasks reached` });
      return;
    }

    setTasks([
      ...tasks,
      {
        title: '',
        description: '',
        priority: 'medium',
        tags: [],
        due_date_offset: tasks.length // Default to next day
      }
    ]);
  };

  const removeTask = (index: number) => {
    if (tasks.length === 1) {
      setErrors({ tasks: 'Template must contain at least one task' });
      return;
    }

    setTasks(tasks.filter((_, i) => i !== index));
  };

  const updateTask = (index: number, field: keyof TaskDefinition, value: any) => {
    const updatedTasks = [...tasks];
    updatedTasks[index] = {
      ...updatedTasks[index],
      [field]: value
    };
    setTasks(updatedTasks);

    // Clear field-specific error
    const errorKey = `task_${index}_${field}`;
    if (errors[errorKey]) {
      setErrors({ ...errors, [errorKey]: '' });
    }
  };

  const updateTaskTag = (taskIndex: number, tagIndex: number, value: string) => {
    const updatedTasks = [...tasks];
    const updatedTags = [...(updatedTasks[taskIndex].tags || [])];
    updatedTags[tagIndex] = value;
    updatedTasks[taskIndex] = {
      ...updatedTasks[taskIndex],
      tags: updatedTags
    };
    setTasks(updatedTasks);
  };

  const addTaskTag = (taskIndex: number) => {
    const updatedTasks = [...tasks];
    updatedTasks[taskIndex] = {
      ...updatedTasks[taskIndex],
      tags: [...(updatedTasks[taskIndex].tags || []), '']
    };
    setTasks(updatedTasks);
  };

  const removeTaskTag = (taskIndex: number, tagIndex: number) => {
    const updatedTasks = [...tasks];
    updatedTasks[taskIndex] = {
      ...updatedTasks[taskIndex],
      tags: (updatedTasks[taskIndex].tags || []).filter((_, i) => i !== tagIndex)
    };
    setTasks(updatedTasks);
  };

  // === Form Submission ===
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);

    try {
      await onSubmit({
        name: name.trim(),
        description: description.trim() || undefined,
        tasks_definition: tasks.map(task => ({
          ...task,
          title: task.title.trim(),
          description: task.description?.trim() || undefined,
          tags: task.tags?.filter(t => t.trim()).map(t => t.trim())
        }))
      });
    } catch (error) {
      console.error('Template submission error:', error);
      setErrors({ submit: 'Failed to save template. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Header Section */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-900">
          {initialData?.id ? 'Edit Template' : 'Create Template'}
        </h2>

        {/* Template Name */}
        <div>
          <label htmlFor="template-name" className="block text-sm font-medium text-gray-700 mb-1">
            Template Name <span className="text-red-500">*</span>
          </label>
          <input
            id="template-name"
            type="text"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              if (errors.name) setErrors({ ...errors, name: '' });
            }}
            placeholder="e.g., Client Onboarding, Weekly Sprint"
            maxLength={100}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500
                      ${errors.name ? 'border-red-500' : 'border-gray-300'}`}
            aria-invalid={!!errors.name}
            aria-describedby={errors.name ? 'name-error' : undefined}
          />
          {errors.name && (
            <p id="name-error" className="mt-1 text-sm text-red-600">{errors.name}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">{name.length}/100 characters</p>
        </div>

        {/* Template Description */}
        <div>
          <label htmlFor="template-description" className="block text-sm font-medium text-gray-700 mb-1">
            Description (Optional)
          </label>
          <textarea
            id="template-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the purpose of this template"
            maxLength={500}
            rows={2}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <p className="mt-1 text-xs text-gray-500">{description.length}/500 characters</p>
        </div>

        {/* Detected Placeholders */}
        {detectedPlaceholders.length > 0 && (
          <div className={`p-4 rounded-lg ${
            detectedPlaceholders.length > MAX_PLACEHOLDERS ? 'bg-red-50 border border-red-200' : 'bg-blue-50 border border-blue-200'
          }`}>
            <div className="flex items-start gap-2">
              {detectedPlaceholders.length > MAX_PLACEHOLDERS && (
                <ExclamationCircleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              )}
              <div className="flex-1">
                <p className={`text-sm font-medium ${
                  detectedPlaceholders.length > MAX_PLACEHOLDERS ? 'text-red-900' : 'text-blue-900'
                }`}>
                  Detected Placeholders ({detectedPlaceholders.length}/{MAX_PLACEHOLDERS})
                </p>
                <div className="flex flex-wrap gap-2 mt-2">
                  {detectedPlaceholders.map((placeholder) => (
                    <code
                      key={placeholder}
                      className="px-2 py-1 bg-white border border-gray-300 rounded text-xs font-mono"
                    >
                      {`{{${placeholder}}}`}
                    </code>
                  ))}
                </div>
                {detectedPlaceholders.length > MAX_PLACEHOLDERS && (
                  <p className="mt-2 text-xs text-red-700">
                    Please reduce the number of unique placeholders to {MAX_PLACEHOLDERS} or fewer.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {errors.placeholders && (
          <p className="text-sm text-red-600">{errors.placeholders}</p>
        )}
      </div>

      {/* Tasks Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Tasks ({tasks.length}/{MAX_TASKS})
          </h3>
          <button
            type="button"
            onClick={addTask}
            disabled={tasks.length >= MAX_TASKS}
            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-blue-600
                     bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100
                     disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PlusIcon className="h-4 w-4" />
            Add Task
          </button>
        </div>

        {errors.tasks && (
          <p className="text-sm text-red-600">{errors.tasks}</p>
        )}

        {/* Task List */}
        <div className="space-y-4">
          {tasks.map((task, taskIndex) => (
            <div
              key={taskIndex}
              className="p-4 border border-gray-200 rounded-lg bg-gray-50 space-y-3"
            >
              {/* Task Header */}
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium text-gray-700">Task {taskIndex + 1}</h4>
                {tasks.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeTask(taskIndex)}
                    className="p-1 text-red-600 hover:text-red-700"
                    aria-label={`Remove task ${taskIndex + 1}`}
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                )}
              </div>

              {/* Task Title */}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Title <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={task.title}
                  onChange={(e) => updateTask(taskIndex, 'title', e.target.value)}
                  placeholder="e.g., {{CLIENT_NAME}} - Initial Meeting"
                  className={`w-full px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-blue-500
                            ${errors[`task_${taskIndex}_title`] ? 'border-red-500' : 'border-gray-300'}`}
                />
                {errors[`task_${taskIndex}_title`] && (
                  <p className="mt-1 text-xs text-red-600">{errors[`task_${taskIndex}_title`]}</p>
                )}
              </div>

              {/* Task Description */}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={task.description || ''}
                  onChange={(e) => updateTask(taskIndex, 'description', e.target.value)}
                  placeholder="Optional task description (supports {{PLACEHOLDERS}})"
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Priority and Due Date Offset */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={task.priority}
                    onChange={(e) => updateTask(taskIndex, 'priority', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Due Date Offset (days)
                  </label>
                  <input
                    type="number"
                    value={task.due_date_offset || 0}
                    onChange={(e) => updateTask(taskIndex, 'due_date_offset', parseInt(e.target.value) || 0)}
                    min={0}
                    max={365}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Tags */}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Tags
                </label>
                <div className="space-y-2">
                  {(task.tags || []).map((tag, tagIndex) => (
                    <div key={tagIndex} className="flex gap-2">
                      <input
                        type="text"
                        value={tag}
                        onChange={(e) => updateTaskTag(taskIndex, tagIndex, e.target.value)}
                        placeholder="e.g., onboarding, {{CLIENT_NAME}}"
                        className="flex-1 px-3 py-1.5 border border-gray-300 rounded-md text-sm"
                      />
                      <button
                        type="button"
                        onClick={() => removeTaskTag(taskIndex, tagIndex)}
                        className="px-2 text-red-600 hover:text-red-700"
                        aria-label="Remove tag"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={() => addTaskTag(taskIndex)}
                    className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                  >
                    + Add Tag
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Submit Error */}
      {errors.submit && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{errors.submit}</p>
        </div>
      )}

      {/* Form Actions */}
      <div className="flex gap-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border
                   border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50
                   disabled:cursor-not-allowed"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg
                   hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Saving...' : (initialData?.id ? 'Update Template' : 'Create Template')}
        </button>
      </div>

      {/* Helpful Tip */}
      <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
        <p className="text-xs text-gray-600">
          <strong>Tip:</strong> Use <code className="px-1 bg-white border rounded">{'{{PLACEHOLDER}}'}</code> syntax
          in titles, descriptions, and tags. Placeholders must be UPPERCASE with underscores (e.g., CLIENT_NAME, PROJECT_TYPE).
        </p>
      </div>
    </form>
  );
}
