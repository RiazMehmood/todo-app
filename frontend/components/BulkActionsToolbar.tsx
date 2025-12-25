/**
 * BulkActionsToolbar Component - Toolbar for performing bulk operations on tasks
 *
 * Implements: User Story 2 (Templates & Bulk Operations) from intermediate-advanced-features.md
 * Contract: specs/005-cloud-native-deployment/contracts/bulk-operations-api.yaml
 */

'use client'

import { useState } from 'react'

interface BulkActionsToolbarProps {
  /** Array of selected task IDs */
  selectedTaskIds: number[]
  /** Callback to clear selection */
  onClearSelection: () => void
  /** Callback for bulk update operations */
  onBulkUpdate: (updates: { priority?: string; status?: string; tags?: string[] }) => Promise<void>
  /** Callback for bulk delete operation */
  onBulkDelete: () => Promise<void>
}

export default function BulkActionsToolbar({
  selectedTaskIds,
  onClearSelection,
  onBulkUpdate,
  onBulkDelete
}: BulkActionsToolbarProps) {
  // State for dropdowns and inputs
  const [showPriorityMenu, setShowPriorityMenu] = useState(false)
  const [showStatusMenu, setShowStatusMenu] = useState(false)
  const [showTagsInput, setShowTagsInput] = useState(false)
  const [tagsInput, setTagsInput] = useState('')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  const selectedCount = selectedTaskIds.length
  const hasSelection = selectedCount > 0

  // Handle priority update
  const handlePriorityUpdate = async (priority: 'low' | 'medium' | 'high') => {
    try {
      setIsProcessing(true)
      await onBulkUpdate({ priority })
      setShowPriorityMenu(false)
    } catch (error) {
      console.error('Failed to update priority:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  // Handle status update
  const handleStatusUpdate = async (status: 'pending' | 'in_progress' | 'completed') => {
    try {
      setIsProcessing(true)
      await onBulkUpdate({ status })
      setShowStatusMenu(false)
    } catch (error) {
      console.error('Failed to update status:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  // Handle tags update
  const handleTagsSubmit = async () => {
    if (!tagsInput.trim()) return

    try {
      setIsProcessing(true)
      const tags = tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0)
      await onBulkUpdate({ tags })
      setTagsInput('')
      setShowTagsInput(false)
    } catch (error) {
      console.error('Failed to add tags:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  // Handle delete
  const handleDelete = async () => {
    try {
      setIsProcessing(true)
      await onBulkDelete()
      setShowDeleteConfirm(false)
    } catch (error) {
      console.error('Failed to delete tasks:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  // Don't render if no selection
  if (!hasSelection) {
    return null
  }

  return (
    <>
      {/* Sticky Toolbar at Bottom */}
      <div
        className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-blue-600 shadow-lg z-40"
        role="toolbar"
        aria-label="Bulk actions toolbar"
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          {/* Mobile Layout (Stack) */}
          <div className="flex flex-col gap-3 md:hidden">
            {/* Selection Count and Clear */}
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-900">
                {selectedCount} task{selectedCount !== 1 ? 's' : ''} selected
              </span>
              <button
                onClick={onClearSelection}
                className="text-sm text-gray-600 hover:text-gray-900"
                aria-label="Clear selection"
                disabled={isProcessing}
              >
                Clear
              </button>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-2">
              {/* Priority Button */}
              <div className="relative flex-1 min-w-[120px]">
                <button
                  onClick={() => setShowPriorityMenu(!showPriorityMenu)}
                  className="w-full px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 disabled:opacity-50"
                  aria-label="Update priority"
                  aria-expanded={showPriorityMenu}
                  disabled={isProcessing}
                >
                  Set Priority
                </button>
                {showPriorityMenu && (
                  <div className="absolute bottom-full mb-2 left-0 w-full bg-white border border-gray-300 rounded-lg shadow-lg">
                    <button
                      onClick={() => handlePriorityUpdate('high')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 text-red-700"
                      disabled={isProcessing}
                    >
                      High
                    </button>
                    <button
                      onClick={() => handlePriorityUpdate('medium')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 text-yellow-700"
                      disabled={isProcessing}
                    >
                      Medium
                    </button>
                    <button
                      onClick={() => handlePriorityUpdate('low')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 text-gray-700"
                      disabled={isProcessing}
                    >
                      Low
                    </button>
                  </div>
                )}
              </div>

              {/* Status Button */}
              <div className="relative flex-1 min-w-[120px]">
                <button
                  onClick={() => setShowStatusMenu(!showStatusMenu)}
                  className="w-full px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 disabled:opacity-50"
                  aria-label="Update status"
                  aria-expanded={showStatusMenu}
                  disabled={isProcessing}
                >
                  Set Status
                </button>
                {showStatusMenu && (
                  <div className="absolute bottom-full mb-2 left-0 w-full bg-white border border-gray-300 rounded-lg shadow-lg">
                    <button
                      onClick={() => handleStatusUpdate('pending')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
                      disabled={isProcessing}
                    >
                      Pending
                    </button>
                    <button
                      onClick={() => handleStatusUpdate('in_progress')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
                      disabled={isProcessing}
                    >
                      In Progress
                    </button>
                    <button
                      onClick={() => handleStatusUpdate('completed')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
                      disabled={isProcessing}
                    >
                      Completed
                    </button>
                  </div>
                )}
              </div>

              {/* Add Tags Button */}
              <button
                onClick={() => setShowTagsInput(!showTagsInput)}
                className="flex-1 min-w-[120px] px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 disabled:opacity-50"
                aria-label="Add tags"
                disabled={isProcessing}
              >
                Add Tags
              </button>

              {/* Delete Button */}
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="flex-1 min-w-[120px] px-3 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 disabled:opacity-50"
                aria-label={`Delete ${selectedCount} selected tasks`}
                disabled={isProcessing}
              >
                Delete
              </button>
            </div>

            {/* Tags Input (Mobile) */}
            {showTagsInput && (
              <div className="flex gap-2">
                <input
                  type="text"
                  value={tagsInput}
                  onChange={(e) => setTagsInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      handleTagsSubmit()
                    }
                  }}
                  placeholder="tag1, tag2, tag3"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  aria-label="Enter tags separated by commas"
                  disabled={isProcessing}
                />
                <button
                  onClick={handleTagsSubmit}
                  className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  disabled={!tagsInput.trim() || isProcessing}
                >
                  Add
                </button>
              </div>
            )}
          </div>

          {/* Desktop Layout (Horizontal) */}
          <div className="hidden md:flex items-center justify-between gap-4">
            {/* Selection Count */}
            <div className="flex items-center gap-4">
              <span className="text-sm font-semibold text-gray-900">
                {selectedCount} task{selectedCount !== 1 ? 's' : ''} selected
              </span>
              <button
                onClick={onClearSelection}
                className="text-sm text-gray-600 hover:text-gray-900"
                aria-label="Clear selection"
                disabled={isProcessing}
              >
                Clear Selection
              </button>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              {/* Priority Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowPriorityMenu(!showPriorityMenu)}
                  className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 flex items-center gap-2 disabled:opacity-50"
                  aria-label="Update priority"
                  aria-expanded={showPriorityMenu}
                  disabled={isProcessing}
                >
                  Set Priority
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {showPriorityMenu && (
                  <div className="absolute bottom-full mb-2 left-0 bg-white border border-gray-300 rounded-lg shadow-lg min-w-[150px]">
                    <button
                      onClick={() => handlePriorityUpdate('high')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 text-red-700 flex items-center gap-2"
                      disabled={isProcessing}
                    >
                      <span className="w-2 h-2 rounded-full bg-red-600"></span>
                      High
                    </button>
                    <button
                      onClick={() => handlePriorityUpdate('medium')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 text-yellow-700 flex items-center gap-2"
                      disabled={isProcessing}
                    >
                      <span className="w-2 h-2 rounded-full bg-yellow-600"></span>
                      Medium
                    </button>
                    <button
                      onClick={() => handlePriorityUpdate('low')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 text-gray-700 flex items-center gap-2"
                      disabled={isProcessing}
                    >
                      <span className="w-2 h-2 rounded-full bg-gray-600"></span>
                      Low
                    </button>
                  </div>
                )}
              </div>

              {/* Status Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowStatusMenu(!showStatusMenu)}
                  className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 flex items-center gap-2 disabled:opacity-50"
                  aria-label="Update status"
                  aria-expanded={showStatusMenu}
                  disabled={isProcessing}
                >
                  Set Status
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {showStatusMenu && (
                  <div className="absolute bottom-full mb-2 left-0 bg-white border border-gray-300 rounded-lg shadow-lg min-w-[150px]">
                    <button
                      onClick={() => handleStatusUpdate('pending')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
                      disabled={isProcessing}
                    >
                      Pending
                    </button>
                    <button
                      onClick={() => handleStatusUpdate('in_progress')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
                      disabled={isProcessing}
                    >
                      In Progress
                    </button>
                    <button
                      onClick={() => handleStatusUpdate('completed')}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
                      disabled={isProcessing}
                    >
                      Completed
                    </button>
                  </div>
                )}
              </div>

              {/* Add Tags */}
              {!showTagsInput ? (
                <button
                  onClick={() => setShowTagsInput(true)}
                  className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 disabled:opacity-50"
                  aria-label="Add tags"
                  disabled={isProcessing}
                >
                  Add Tags
                </button>
              ) : (
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={tagsInput}
                    onChange={(e) => setTagsInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        handleTagsSubmit()
                      }
                      if (e.key === 'Escape') {
                        setShowTagsInput(false)
                        setTagsInput('')
                      }
                    }}
                    placeholder="tag1, tag2, tag3"
                    className="w-48 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    aria-label="Enter tags separated by commas"
                    autoFocus
                    disabled={isProcessing}
                  />
                  <button
                    onClick={handleTagsSubmit}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    disabled={!tagsInput.trim() || isProcessing}
                  >
                    Add
                  </button>
                  <button
                    onClick={() => {
                      setShowTagsInput(false)
                      setTagsInput('')
                    }}
                    className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200"
                    disabled={isProcessing}
                  >
                    Cancel
                  </button>
                </div>
              )}

              {/* Delete Button */}
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 flex items-center gap-2 disabled:opacity-50"
                aria-label={`Delete ${selectedCount} selected tasks`}
                disabled={isProcessing}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete Selected
              </button>
            </div>
          </div>

          {/* Processing Indicator */}
          {isProcessing && (
            <div className="mt-2 flex items-center gap-2 text-sm text-gray-600">
              <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin"></div>
              Processing...
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          role="dialog"
          aria-labelledby="delete-dialog-title"
          aria-modal="true"
        >
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 id="delete-dialog-title" className="text-lg font-semibold text-gray-900 mb-4">
              Delete {selectedCount} Task{selectedCount !== 1 ? 's' : ''}?
            </h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete {selectedCount} selected task{selectedCount !== 1 ? 's' : ''}?
              This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                disabled={isProcessing}
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2 disabled:opacity-50"
                disabled={isProcessing}
              >
                {isProcessing && (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                )}
                Delete {selectedCount} Task{selectedCount !== 1 ? 's' : ''}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
