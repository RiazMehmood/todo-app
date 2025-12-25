'use client';

/**
 * SavedSearches Component
 *
 * Dropdown for managing and executing saved searches.
 * Shows list of user's saved searches with ability to execute or delete.
 */

import { useState, useEffect } from 'react';
import { BookmarkIcon, TrashIcon } from '@heroicons/react/24/outline';

interface SavedSearch {
  id: string;
  name: string;
  query_params: {
    query?: string;
    filters?: any;
    sort_by?: string;
    sort_order?: string;
  };
  created_at: string;
}

interface SavedSearchesProps {
  userId: string;
  onExecute: (search: SavedSearch) => void;
  onSaveNew: () => void;
}

export function SavedSearches({ userId, onExecute, onSaveNew }: SavedSearchesProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch saved searches
  const fetchSavedSearches = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`/api/${userId}/saved-searches`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSearches(data);
      } else {
        setError('Failed to load saved searches');
      }
    } catch (err) {
      console.error('Error fetching saved searches:', err);
      setError('Failed to load saved searches');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchSavedSearches();
    }
  }, [isOpen, userId]);

  const handleDelete = async (searchId: string, searchName: string) => {
    if (!confirm(`Delete saved search "${searchName}"?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/${userId}/saved-searches/${searchId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
      });

      if (response.ok) {
        // Refresh list
        fetchSavedSearches();
      } else {
        alert('Failed to delete saved search');
      }
    } catch (err) {
      console.error('Error deleting saved search:', err);
      alert('Failed to delete saved search');
    }
  };

  const handleExecute = (search: SavedSearch) => {
    onExecute(search);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      {/* Dropdown Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300
                 rounded-lg hover:bg-gray-50 transition-colors duration-200
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <BookmarkIcon className="h-5 w-5 text-gray-600" />
        <span className="text-sm font-medium text-gray-700">Saved Searches</span>
        {searches.length > 0 && (
          <span className="px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded-full">
            {searches.length}
          </span>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute z-20 mt-2 w-80 bg-white border border-gray-300
                      rounded-lg shadow-xl overflow-hidden">
          {/* Header */}
          <div className="px-4 py-3 bg-gray-50 border-b flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900">Saved Searches</h3>
            <button
              onClick={() => {
                onSaveNew();
                setIsOpen(false);
              }}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium"
            >
              + Save Current
            </button>
          </div>

          {/* Content */}
          <div className="max-h-96 overflow-y-auto">
            {loading && (
              <div className="px-4 py-8 text-center text-sm text-gray-500">
                Loading saved searches...
              </div>
            )}

            {error && (
              <div className="px-4 py-8 text-center text-sm text-red-600">
                {error}
              </div>
            )}

            {!loading && !error && searches.length === 0 && (
              <div className="px-4 py-8 text-center">
                <BookmarkIcon className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No saved searches yet</p>
                <button
                  onClick={() => {
                    onSaveNew();
                    setIsOpen(false);
                  }}
                  className="mt-3 text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Save your first search
                </button>
              </div>
            )}

            {!loading && !error && searches.length > 0 && (
              <div className="divide-y">
                {searches.map((search) => (
                  <div
                    key={search.id}
                    className="px-4 py-3 hover:bg-gray-50 transition-colors duration-150"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <button
                        onClick={() => handleExecute(search)}
                        className="flex-1 text-left group"
                      >
                        <div className="text-sm font-medium text-gray-900 group-hover:text-blue-600">
                          {search.name}
                        </div>
                        {search.query_params.query && (
                          <div className="text-xs text-gray-500 mt-1 truncate">
                            Query: "{search.query_params.query}"
                          </div>
                        )}
                        <div className="text-xs text-gray-400 mt-1">
                          {new Date(search.created_at).toLocaleDateString()}
                        </div>
                      </button>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(search.id, search.name);
                        }}
                        className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                        title="Delete"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-2 bg-gray-50 border-t">
            <button
              onClick={() => setIsOpen(false)}
              className="w-full text-center text-xs text-gray-600 hover:text-gray-900"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
