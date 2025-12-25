/**
 * Templates Page - Task template management interface
 *
 * Implements: User Story 2 (Templates & Bulk Operations) from intermediate-advanced-features.md
 * Contract: specs/005-cloud-native-deployment/contracts/templates-api.yaml
 */

'use client'

import { useState, useEffect } from 'react'
import { TemplateForm } from '@/components/TemplateForm'
import InstantiateTemplateDialog from '@/components/InstantiateTemplateDialog'

interface TaskTemplate {
  id: string
  user_id: string
  name: string
  description: string | null
  tasks_definition: Array<{
    title: string
    description?: string
    priority?: 'low' | 'medium' | 'high'
    tags?: string[]
    due_date_offset?: number
  }>
  placeholders: string[]
  created_at: string
  updated_at: string
}

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<TaskTemplate[]>([])
  const [filteredTemplates, setFilteredTemplates] = useState<TaskTemplate[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // UI state
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<TaskTemplate | null>(null)
  const [deletingTemplateId, setDeletingTemplateId] = useState<string | null>(null)
  const [instantiatingTemplateId, setInstantiatingTemplateId] = useState<string | null>(null)

  // Get user_id from auth (placeholder - replace with actual auth)
  const userId = 'user123' // TODO: Get from auth context

  // Fetch templates on mount
  useEffect(() => {
    fetchTemplates()
  }, [])

  // Filter templates when search query changes
  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = templates.filter(template =>
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (template.description?.toLowerCase().includes(searchQuery.toLowerCase()))
      )
      setFilteredTemplates(filtered)
    } else {
      setFilteredTemplates(templates)
    }
  }, [searchQuery, templates])

  const fetchTemplates = async () => {
    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch(`/api/${userId}/templates`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`, // TODO: Get from auth
        },
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch templates: ${response.statusText}`)
      }

      const data = await response.json()
      setTemplates(data)
      setFilteredTemplates(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load templates')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateTemplate = async (templateData: any) => {
    try {
      const response = await fetch(`/api/${userId}/templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(templateData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create template')
      }

      const newTemplate = await response.json()
      setTemplates([newTemplate, ...templates])
      setShowCreateForm(false)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create template')
    }
  }

  const handleUpdateTemplate = async (templateData: any) => {
    if (!editingTemplate) return

    try {
      const response = await fetch(`/api/${userId}/templates/${editingTemplate.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(templateData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to update template')
      }

      const updatedTemplate = await response.json()
      setTemplates(templates.map(t => t.id === updatedTemplate.id ? updatedTemplate : t))
      setEditingTemplate(null)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update template')
    }
  }

  const handleDeleteTemplate = async (templateId: string) => {
    try {
      const response = await fetch(`/api/${userId}/templates/${templateId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to delete template')
      }

      setTemplates(templates.filter(t => t.id !== templateId))
      setDeletingTemplateId(null)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete template')
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-gray-600">Loading templates...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h3 className="text-red-800 font-semibold mb-2">Error Loading Templates</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={fetchTemplates}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Task Templates</h1>
          <p className="text-gray-600">
            Create reusable templates for recurring task sets
          </p>
        </div>

        {/* Search and Create Button */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          {/* Search Bar */}
          <div className="relative flex-1 max-w-md">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search templates..."
              aria-label="Search templates"
              className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                aria-label="Clear search"
              >
                ✕
              </button>
            )}
          </div>

          {/* Create New Template Button */}
          <button
            onClick={() => setShowCreateForm(true)}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 whitespace-nowrap"
            aria-label="Create new template"
          >
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
            Create Template
          </button>
        </div>

        {/* Results Count */}
        {searchQuery && (
          <div className="mb-4 text-gray-600">
            Found {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''}
          </div>
        )}

        {/* Empty State */}
        {filteredTemplates.length === 0 && !searchQuery && (
          <div className="text-center py-16 bg-white rounded-lg border border-gray-200">
            <svg
              className="mx-auto w-16 h-16 text-gray-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No templates yet</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Create your first template to save time on recurring task sets
            </p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create Your First Template
            </button>
          </div>
        )}

        {/* No Search Results */}
        {filteredTemplates.length === 0 && searchQuery && (
          <div className="text-center py-16 bg-white rounded-lg border border-gray-200">
            <p className="text-gray-600">
              No templates found matching &quot;{searchQuery}&quot;
            </p>
            <button
              onClick={() => setSearchQuery('')}
              className="mt-4 text-blue-600 hover:text-blue-700"
            >
              Clear search
            </button>
          </div>
        )}

        {/* Templates Grid - Responsive: 1 col mobile, 2 cols tablet, 3 cols desktop */}
        {filteredTemplates.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template) => (
              <div
                key={template.id}
                className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
              >
                {/* Template Header */}
                <div className="mb-4">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {template.name}
                  </h3>
                  {template.description && (
                    <p className="text-gray-600 text-sm line-clamp-2">
                      {template.description}
                    </p>
                  )}
                </div>

                {/* Template Stats */}
                <div className="flex gap-4 mb-4 text-sm text-gray-600">
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
                    <span>{template.tasks_definition.length} tasks</span>
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

                {/* Placeholders List */}
                {template.placeholders.length > 0 && (
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-2">
                      {template.placeholders.map((placeholder) => (
                        <span
                          key={placeholder}
                          className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded font-mono"
                        >
                          {'{{' + placeholder + '}}'}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Created Date */}
                <div className="text-xs text-gray-500 mb-4">
                  Created {formatDate(template.created_at)}
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => setInstantiatingTemplateId(template.id)}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                    aria-label={`Instantiate ${template.name} template`}
                  >
                    Instantiate
                  </button>
                  <button
                    onClick={() => setEditingTemplate(template)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded hover:bg-gray-200"
                    aria-label={`Edit ${template.name} template`}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => setDeletingTemplateId(template.id)}
                    className="px-4 py-2 bg-red-50 text-red-600 text-sm rounded hover:bg-red-100"
                    aria-label={`Delete ${template.name} template`}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create Template Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
                <h2 className="text-2xl font-bold text-gray-900">Create Template</h2>
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="text-gray-400 hover:text-gray-600"
                  aria-label="Close"
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
              <div className="p-6">
                <TemplateForm
                  userId={userId}
                  onSubmit={handleCreateTemplate}
                  onCancel={() => setShowCreateForm(false)}
                />
              </div>
            </div>
          </div>
        )}

        {/* Edit Template Modal */}
        {editingTemplate && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
                <h2 className="text-2xl font-bold text-gray-900">Edit Template</h2>
                <button
                  onClick={() => setEditingTemplate(null)}
                  className="text-gray-400 hover:text-gray-600"
                  aria-label="Close"
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
              <div className="p-6">
                <TemplateForm
                  userId={userId}
                  initialData={editingTemplate ? {
                    id: editingTemplate.id,
                    name: editingTemplate.name,
                    description: editingTemplate.description ?? undefined,
                    tasks_definition: editingTemplate.tasks_definition.map(task => ({
                      title: task.title,
                      description: task.description,
                      priority: task.priority ?? 'medium',
                      tags: task.tags,
                      due_date_offset: task.due_date_offset
                    }))
                  } : undefined}
                  onSubmit={handleUpdateTemplate}
                  onCancel={() => setEditingTemplate(null)}
                />
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Dialog */}
        {deletingTemplateId && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Delete Template?
              </h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to delete this template? This action cannot be undone.
                Tasks created from this template will not be affected.
              </p>
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setDeletingTemplateId(null)}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleDeleteTemplate(deletingTemplateId)}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Delete Template
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Instantiate Template Dialog */}
        {instantiatingTemplateId && (
          <InstantiateTemplateDialog
            template={templates.find(t => t.id === instantiatingTemplateId)!}
            userId={userId}
            onClose={() => setInstantiatingTemplateId(null)}
            onSuccess={(tasksCount) => {
              alert(`Successfully created ${tasksCount} tasks from template!`)
              setInstantiatingTemplateId(null)
              // Optionally refresh tasks list or redirect to tasks page
            }}
          />
        )}
      </div>
    </div>
  )
}
