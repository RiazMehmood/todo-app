'use client';

/**
 * Search Page
 *
 * Advanced task search interface with:
 * - Full-text search with boolean operators
 * - Multi-criteria filtering
 * - Saved searches management
 * - Search term highlighting in results
 * - Pagination
 */

import { useState, useEffect, ReactElement } from 'react';
import { SearchBar } from '@/components/SearchBar';
import { FilterPanel } from '@/components/FilterPanel';
import { SavedSearches } from '@/components/SavedSearches';
import { SaveSearchDialog } from '@/components/SaveSearchDialog';

interface Task {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  tags?: string[];
  due_date?: string;
  created_at: string;
  updated_at: string;
}

interface SearchResponse {
  tasks: Task[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

interface SavedSearch {
  id: string;
  name: string;
  query_params: {
    query?: string;
    filters?: any;
    sort_by?: string;
    sort_order?: string;
  };
}

export default function SearchPage() {
  // Get user ID (from auth context or session)
  const userId = 'user123'; // TODO: Get from auth context

  // Search state
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<any>({});
  const [sortBy, setSortBy] = useState('relevance');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(1);
  const [perPage] = useState(50);

  // Results state
  const [results, setResults] = useState<Task[]>([]);
  const [totalResults, setTotalResults] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // UI state
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Perform search
  const performSearch = async () => {
    setLoading(true);
    setError('');
    setHasSearched(true);

    try {
      const response = await fetch(`/api/${userId}/tasks/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
        body: JSON.stringify({
          query: query || null,
          filters,
          sort_by: sortBy,
          sort_order: sortOrder,
          page,
          per_page: perPage
        })
      });

      if (response.ok) {
        const data: SearchResponse = await response.json();
        setResults(data.tasks);
        setTotalResults(data.total);
        setTotalPages(data.total_pages);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Search failed');
      }
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to perform search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Execute saved search
  const handleExecuteSavedSearch = (search: SavedSearch) => {
    setQuery(search.query_params.query || '');
    setFilters(search.query_params.filters || {});
    setSortBy(search.query_params.sort_by || 'relevance');
    setSortOrder(search.query_params.sort_order || 'desc');
    setPage(1);

    // Trigger search
    setTimeout(() => performSearch(), 100);
  };

  // Save current search
  const handleSaveSearch = async (name: string) => {
    const response = await fetch(`/api/${userId}/saved-searches`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
      body: JSON.stringify({
        name,
        query_params: {
          query,
          filters,
          sort_by: sortBy,
          sort_order: sortOrder
        }
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to save search');
    }
  };

  // Highlight search terms in text
  const highlightText = (text: string, searchQuery: string): ReactElement => {
    if (!searchQuery || !text) {
      return <>{text}</>;
    }

    // Extract words from query (remove operators)
    const words = searchQuery
      .replace(/\b(AND|OR|NOT)\b/gi, '')
      .split(/\s+/)
      .filter(w => w.length > 0);

    if (words.length === 0) {
      return <>{text}</>;
    }

    // Create regex pattern
    const pattern = new RegExp(`(${words.join('|')})`, 'gi');
    const parts = text.split(pattern);

    return (
      <>
        {parts.map((part, index) => {
          const isMatch = words.some(w => w.toLowerCase() === part.toLowerCase());
          return isMatch ? (
            <mark key={index} className="bg-yellow-200 font-medium">
              {part}
            </mark>
          ) : (
            <span key={index}>{part}</span>
          );
        })}
      </>
    );
  };

  // Auto-search when page changes
  useEffect(() => {
    if (hasSearched) {
      performSearch();
    }
  }, [page]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Search Tasks</h1>
          <p className="text-gray-600">
            Find tasks using full-text search, filters, and saved searches
          </p>
        </div>

        {/* Search Controls */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="space-y-4">
            {/* Search Bar */}
            <SearchBar
              onSearch={(q) => {
                setQuery(q);
                setPage(1);
                setTimeout(() => performSearch(), 100);
              }}
              userId={userId}
              autoFocus
            />

            {/* Filters and Saved Searches */}
            <div className="flex gap-3">
              <FilterPanel
                onFilterChange={(f) => {
                  setFilters(f);
                  setPage(1);
                }}
                userId={userId}
              />

              <SavedSearches
                userId={userId}
                onExecute={handleExecuteSavedSearch}
                onSaveNew={() => setShowSaveDialog(true)}
              />

              <button
                onClick={() => setShowSaveDialog(true)}
                disabled={!query && Object.keys(filters).length === 0}
                className="ml-auto px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50
                         border border-blue-200 rounded-lg hover:bg-blue-100
                         disabled:opacity-50 disabled:cursor-not-allowed
                         transition-colors duration-200"
              >
                Save Search
              </button>
            </div>

            {/* Sorting */}
            <div className="flex items-center gap-4 pt-2 border-t">
              <label className="text-sm font-medium text-gray-700">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setPage(1);
                }}
                className="px-3 py-1.5 border border-gray-300 rounded-md text-sm
                         focus:ring-2 focus:ring-blue-500"
              >
                <option value="relevance">Relevance</option>
                <option value="created_at">Created Date</option>
                <option value="updated_at">Updated Date</option>
                <option value="due_date">Due Date</option>
                <option value="priority">Priority</option>
              </select>

              <select
                value={sortOrder}
                onChange={(e) => {
                  setSortOrder(e.target.value);
                  setPage(1);
                }}
                className="px-3 py-1.5 border border-gray-300 rounded-md text-sm
                         focus:ring-2 focus:ring-blue-500"
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results */}
        <div>
          {/* Results Header */}
          {hasSearched && !loading && (
            <div className="mb-4 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Found <span className="font-semibold">{totalResults}</span> task{totalResults !== 1 ? 's' : ''}
                {query && ` for "${query}"`}
              </div>
              {totalPages > 1 && (
                <div className="text-sm text-gray-600">
                  Page {page} of {totalPages}
                </div>
              )}
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-sm text-gray-600">Searching...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          )}

          {/* No Results */}
          {hasSearched && !loading && !error && results.length === 0 && (
            <div className="text-center py-12 bg-white rounded-lg border">
              <p className="text-gray-500">No tasks found matching your search</p>
              <p className="text-sm text-gray-400 mt-2">Try adjusting your search query or filters</p>
            </div>
          )}

          {/* Results List */}
          {!loading && results.length > 0 && (
            <div className="space-y-3">
              {results.map((task) => (
                <div
                  key={task.id}
                  className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md
                           transition-shadow duration-200"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900">
                        {highlightText(task.title, query)}
                      </h3>
                      {task.description && (
                        <p className="text-sm text-gray-600 mt-1">
                          {highlightText(task.description, query)}
                        </p>
                      )}
                      <div className="flex items-center gap-3 mt-3">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          task.status === 'completed' ? 'bg-green-100 text-green-700' :
                          task.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {task.status.replace('_', ' ')}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          task.priority === 'high' ? 'bg-red-100 text-red-700' :
                          task.priority === 'medium' ? 'bg-orange-100 text-orange-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {task.priority}
                        </span>
                        {task.tags && task.tags.length > 0 && (
                          <div className="flex gap-1">
                            {task.tags.map((tag, idx) => (
                              <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    {task.due_date && (
                      <div className="text-xs text-gray-500">
                        Due: {new Date(task.due_date).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && !loading && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border
                         border-gray-300 rounded-md hover:bg-gray-50
                         disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border
                         border-gray-300 rounded-md hover:bg-gray-50
                         disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Save Search Dialog */}
      <SaveSearchDialog
        isOpen={showSaveDialog}
        onClose={() => setShowSaveDialog(false)}
        onSave={handleSaveSearch}
        currentQuery={query}
        currentFilters={filters}
      />
    </div>
  );
}
