/**
 * InstantiateTemplateDialog Component - Modal for creating tasks from template
 *
 * Implements: User Story 2 (Templates & Bulk Operations) from intermediate-advanced-features.md
 * Contract: specs/005-cloud-native-deployment/contracts/templates-api.yaml
 */

'use client'

import { useState, useEffect, useMemo } from 'react'

interface TaskDefinition {
  title: string
  description?: string
  priority?: 'low' | 'medium' | 'high'
  tags?: string[]
  due_date_offset?: number
}

interface TaskTemplate {
  id: string
  user_id: string
  name: string
  description: string | null
  tasks_definition: TaskDefinition[]
  placeholders: string[]
  created_at: string
  updated_at: string
}

interface InstantiateTemplateDialogProps {
  /** Template to instantiate */
  template: TaskTemplate
  /** Callback when dialog should close */
  onClose: () => void
  /** Callback when template instantiation succeeds */
  onSuccess: (createdTasksCount: number) => void
  /** User ID for API calls */
  userId: string
}

export default function InstantiateTemplateDialog({
  template,
  onClose,
  onSuccess,
  userId
}: InstantiateTemplateDialogProps) {
  // Form state
  const [placeholderValues, setPlaceholderValues] = useState<Record<string, string>>({})
  const [baseDueDate, setBaseDueDate] = useState<string>('')

  // UI state
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPreview, setShowPreview] = useState(false)

  // Initialize placeholder values with empty strings
  useEffect(() => {
    const initialValues: Record<string, string> = {}
    template.placeholders.forEach(placeholder => {
      initialValues[placeholder] = ''
    })
    setPlaceholderValues(initialValues)
  }, [template.placeholders])

  // Set default base due date to today
  useEffect(() => {
    const today = new Date().toISOString().split('T')[0]
    setBaseDueDate(today)
  }, [])

  // Replace placeholders in text
  const replacePlaceholders = (text: string): string => {
    let result = text
    Object.entries(placeholderValues).forEach(([placeholder, value]) => {
      const pattern = new RegExp(`\\{\\{${placeholder}\\}\\}`, 'g')
      result = result.replace(pattern, value || `{{${placeholder}}}`)
    })
    return result
  }

  // Calculate due date from offset
  const calculateDueDate = (offset: number): string => {
    if (!baseDueDate) return 'Not set'

    const baseDate = new Date(baseDueDate)
    const dueDate = new Date(baseDate)
    dueDate.setDate(dueDate.getDate() + offset)

    return dueDate.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  // Preview tasks with placeholders replaced
  const previewTasks = useMemo(() => {
    return template.tasks_definition.map((taskDef, index) => ({
      index: index + 1,
      title: replacePlaceholders(taskDef.title),
      description: taskDef.description ? replacePlaceholders(taskDef.description) : null,
      priority: taskDef.priority || 'medium',
      tags: taskDef.tags?.map(tag => replacePlaceholders(tag)) || [],
      dueDate: taskDef.due_date_offset !== undefined
        ? calculateDueDate(taskDef.due_date_offset)
        : 'Not set',
      dueDateOffset: taskDef.due_date_offset
    }))
  }, [template.tasks_definition, placeholderValues, baseDueDate])

  // Validation: check if all placeholders have values
  const isValid = useMemo(() => {
    return template.placeholders.every(placeholder =>
      placeholderValues[placeholder]?.trim().length > 0
    ) && baseDueDate.trim().length > 0
  }, [template.placeholders, placeholderValues, baseDueDate])

  // Handle placeholder value change
  const handlePlaceholderChange = (placeholder: string, value: string) => {
    setPlaceholderValues(prev => ({
      ...prev,
      [placeholder]: value
    }))
    setError(null)
  }

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!isValid) {
      setError('Please fill in all placeholder values and select a base due date')
      return
    }

    try {
      setIsSubmitting(true)
      setError(null)

      const response = await fetch(`/api/${userId}/templates/${template.id}/instantiate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          base_due_date: baseDueDate,
          placeholder_values: placeholderValues,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to instantiate template')
      }

      const data = await response.json()
      const tasksCount = data.created_tasks?.length || data.count || 0

      onSuccess(tasksCount)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create tasks from template')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      role="dialog"
      aria-labelledby="dialog-title"
      aria-modal="true"
    >
      <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
          <div>
            <h2 id="dialog-title" className="text-2xl font-bold text-gray-900">
              Instantiate Template
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {template.name}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close dialog"
            disabled={isSubmitting}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Template Description */}
          {template.description && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-blue-900 text-sm">{template.description}</p>
            </div>
          )}

          {/* Template Info */}
          <div className="mb-6 flex gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
              <span>{template.tasks_definition.length} tasks will be created</span>
            </div>
            <div className="flex items-center gap-1">
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                />
              </svg>
              <span>{template.placeholders.length} placeholders</span>
            </div>
          </div>

          {/* Base Due Date */}
          <div className="mb-6">
            <label htmlFor="base-due-date" className="block text-sm font-semibold text-gray-700 mb-2">
              Base Due Date *
            </label>
            <input
              type="date"
              id="base-due-date"
              value={baseDueDate}
              onChange={(e) => setBaseDueDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
              aria-describedby="base-due-date-help"
              disabled={isSubmitting}
            />
            <p id="base-due-date-help" className="text-xs text-gray-500 mt-1">
              Tasks with offset 0 will be due on this date. Other tasks will be offset by their configured days.
            </p>
          </div>

          {/* Placeholder Values */}
          {template.placeholders.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Placeholder Values *
              </h3>
              <div className="space-y-4">
                {template.placeholders.map((placeholder) => (
                  <div key={placeholder}>
                    <label
                      htmlFor={`placeholder-${placeholder}`}
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      <span className="font-mono text-blue-600">{'{{' + placeholder + '}}'}</span>
                    </label>
                    <input
                      type="text"
                      id={`placeholder-${placeholder}`}
                      value={placeholderValues[placeholder] || ''}
                      onChange={(e) => handlePlaceholderChange(placeholder, e.target.value)}
                      placeholder={`Enter value for ${placeholder}`}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                      maxLength={100}
                      aria-required="true"
                      disabled={isSubmitting}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Preview Toggle */}
          <div className="mb-4">
            <button
              type="button"
              onClick={() => setShowPreview(!showPreview)}
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
              aria-expanded={showPreview}
              aria-controls="task-preview"
            >
              <svg
                className={`w-5 h-5 transition-transform ${showPreview ? 'rotate-90' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
              {showPreview ? 'Hide Preview' : 'Show Preview'}
            </button>
          </div>

          {/* Task Preview */}
          {showPreview && (
            <div id="task-preview" className="mb-6 border border-gray-200 rounded-lg p-4 bg-gray-50 max-h-96 overflow-y-auto">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Tasks to be Created
              </h3>
              <div className="space-y-3">
                {previewTasks.map((task) => (
                  <div
                    key={task.index}
                    className="bg-white border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-gray-500">
                          Task {task.index}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded ${
                          task.priority === 'high' ? 'bg-red-100 text-red-700' :
                          task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {task.priority}
                        </span>
                      </div>
                      {task.dueDateOffset !== undefined && (
                        <span className="text-xs text-gray-500">
                          Due: {task.dueDate}
                        </span>
                      )}
                    </div>
                    <h4 className="font-medium text-gray-900 mb-1">
                      {task.title}
                    </h4>
                    {task.description && (
                      <p className="text-sm text-gray-600 mb-2">
                        {task.description}
                      </p>
                    )}
                    {task.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {task.tags.map((tag, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div
              className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg"
              role="alert"
              aria-live="polite"
            >
              <div className="flex items-start gap-3">
                <svg
                  className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!isValid || isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              aria-label={`Create ${template.tasks_definition.length} tasks from template`}
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Creating Tasks...
                </>
              ) : (
                <>
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  Create {template.tasks_definition.length} Tasks
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
