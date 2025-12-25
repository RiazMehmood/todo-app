'use client';

/**
 * SaveSearchDialog Component
 *
 * Modal dialog for saving current search query and filters.
 * Allows user to name and save search for quick access later.
 */

import { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface SaveSearchDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string) => Promise<void>;
  currentQuery?: string;
  currentFilters?: any;
}

export function SaveSearchDialog({
  isOpen,
  onClose,
  onSave,
  currentQuery,
  currentFilters
}: SaveSearchDialogProps) {
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      setError('Please enter a name for this search');
      return;
    }

    setSaving(true);
    setError('');

    try {
      await onSave(name.trim());
      setName('');
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save search');
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    if (!saving) {
      setName('');
      setError('');
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={handleClose}
      />

      {/* Dialog */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Save Search
            </h3>
            <button
              onClick={handleClose}
              disabled={saving}
              className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Preview */}
            <div className="bg-gray-50 rounded-lg p-3 text-sm">
              <div className="font-medium text-gray-700 mb-2">Search Preview:</div>
              {currentQuery && (
                <div className="text-gray-600">
                  <span className="font-medium">Query:</span> "{currentQuery}"
                </div>
              )}
              {currentFilters && Object.keys(currentFilters).length > 0 && (
                <div className="text-gray-600 mt-1">
                  <span className="font-medium">Filters:</span>{' '}
                  {Object.entries(currentFilters).map(([key, value]) => {
                    if (Array.isArray(value) && value.length > 0) {
                      return `${key}: ${value.join(', ')}`;
                    }
                    return null;
                  }).filter(Boolean).join(' | ') || 'None'}
                </div>
              )}
              {!currentQuery && (!currentFilters || Object.keys(currentFilters).length === 0) && (
                <div className="text-gray-500 italic">
                  No search query or filters active
                </div>
              )}
            </div>

            {/* Name Input */}
            <div>
              <label htmlFor="search-name" className="block text-sm font-medium text-gray-700 mb-1">
                Search Name
              </label>
              <input
                id="search-name"
                type="text"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  setError('');
                }}
                placeholder="e.g., High Priority Work Tasks"
                maxLength={100}
                required
                disabled={saving}
                className="w-full px-3 py-2 border border-gray-300 rounded-md
                         focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                         disabled:bg-gray-100 disabled:cursor-not-allowed"
                autoFocus
              />
              <p className="mt-1 text-xs text-gray-500">
                {name.length}/100 characters
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-3">
                {error}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={handleClose}
                disabled={saving}
                className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white
                         border border-gray-300 rounded-md hover:bg-gray-50
                         focus:outline-none focus:ring-2 focus:ring-blue-500
                         disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving || !name.trim()}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600
                         rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2
                         focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? 'Saving...' : 'Save Search'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
