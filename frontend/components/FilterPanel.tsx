'use client';

/**
 * FilterPanel Component
 *
 * Multi-select filter panel for task search with:
 * - Status filter (pending, in_progress, completed)
 * - Priority filter (low, medium, high)
 * - Tags filter (user's tags)
 * - Date range filter
 */

import { useState, useEffect } from 'react';
import { FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface Filters {
  status?: string[];
  priority?: string[];
  tags?: string[];
  date_filter?: string;
  custom_start?: string;
  custom_end?: string;
  created_after?: string;
  created_before?: string;
  due_after?: string;
  due_before?: string;
}

interface FilterPanelProps {
  onFilterChange: (filters: Filters) => void;
  userId: string;
}

export function FilterPanel({ onFilterChange, userId }: FilterPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [filters, setFilters] = useState<Filters>({});
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  // Fetch available tags from user's tasks
  useEffect(() => {
    const fetchTags = async () => {
      try {
        // This would be a dedicated endpoint, but for now we'll use search suggestions
        const response = await fetch(
          `/api/${userId}/search/suggestions?prefix=&type=tags`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setAvailableTags(data.suggestions || []);
        }
      } catch (error) {
        console.error('Failed to fetch tags:', error);
      }
    };

    fetchTags();
  }, [userId]);

  const handleStatusToggle = (status: string) => {
    const currentStatuses = filters.status || [];
    const newStatuses = currentStatuses.includes(status)
      ? currentStatuses.filter(s => s !== status)
      : [...currentStatuses, status];

    updateFilter('status', newStatuses.length > 0 ? newStatuses : undefined);
  };

  const handlePriorityToggle = (priority: string) => {
    const currentPriorities = filters.priority || [];
    const newPriorities = currentPriorities.includes(priority)
      ? currentPriorities.filter(p => p !== priority)
      : [...currentPriorities, priority];

    updateFilter('priority', newPriorities.length > 0 ? newPriorities : undefined);
  };

  const handleTagToggle = (tag: string) => {
    const currentTags = filters.tags || [];
    const newTags = currentTags.includes(tag)
      ? currentTags.filter(t => t !== tag)
      : [...currentTags, tag];

    updateFilter('tags', newTags.length > 0 ? newTags : undefined);
  };

  const handleDateFilterChange = (dateFilter: string) => {
    const newFilters = { ...filters, date_filter: dateFilter };

    // Clear custom dates if not custom_range
    if (dateFilter !== 'custom_range') {
      delete newFilters.custom_start;
      delete newFilters.custom_end;
    }

    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const updateFilter = (key: keyof Filters, value: any) => {
    const newFilters = { ...filters, [key]: value };
    if (value === undefined) {
      delete newFilters[key];
    }
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearAllFilters = () => {
    setFilters({});
    onFilterChange({});
  };

  const activeFilterCount = Object.keys(filters).filter(key => {
    const value = filters[key as keyof Filters];
    return value !== undefined && (Array.isArray(value) ? value.length > 0 : true);
  }).length;

  return (
    <div className="relative">
      {/* Filter Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300
                 rounded-lg hover:bg-gray-50 transition-colors duration-200
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <FunnelIcon className="h-5 w-5 text-gray-600" />
        <span className="text-sm font-medium text-gray-700">Filters</span>
        {activeFilterCount > 0 && (
          <span className="px-2 py-0.5 bg-blue-600 text-white text-xs rounded-full">
            {activeFilterCount}
          </span>
        )}
      </button>

      {/* Filter Panel */}
      {isOpen && (
        <div className="absolute z-20 mt-2 w-80 bg-white border border-gray-300
                      rounded-lg shadow-xl p-4 space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900">Filter Tasks</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Status
            </label>
            <div className="space-y-2">
              {['pending', 'in_progress', 'completed'].map((status) => (
                <label key={status} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.status?.includes(status) || false}
                    onChange={() => handleStatusToggle(status)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded
                             focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 capitalize">
                    {status.replace('_', ' ')}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Priority Filter */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Priority
            </label>
            <div className="space-y-2">
              {['low', 'medium', 'high'].map((priority) => (
                <label key={priority} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.priority?.includes(priority) || false}
                    onChange={() => handlePriorityToggle(priority)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded
                             focus:ring-blue-500"
                  />
                  <span className={`text-sm capitalize ${
                    priority === 'high' ? 'text-red-600 font-medium' :
                    priority === 'medium' ? 'text-orange-600 font-medium' :
                    'text-gray-700'
                  }`}>
                    {priority}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Tags Filter */}
          {availableTags.length > 0 && (
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-2">
                Tags
              </label>
              <div className="max-h-32 overflow-y-auto space-y-2 border border-gray-200 rounded p-2">
                {availableTags.slice(0, 20).map((tag) => (
                  <label key={tag} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.tags?.includes(tag) || false}
                      onChange={() => handleTagToggle(tag)}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded
                               focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">{tag}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Date Range Filter */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Date Range
            </label>
            <select
              value={filters.date_filter || ''}
              onChange={(e) => handleDateFilterChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                       text-sm"
            >
              <option value="">All time</option>
              <option value="last_7_days">Last 7 days</option>
              <option value="last_30_days">Last 30 days</option>
              <option value="last_90_days">Last 90 days</option>
              <option value="custom_range">Custom range...</option>
            </select>

            {/* Custom Date Range Inputs */}
            {filters.date_filter === 'custom_range' && (
              <div className="mt-2 space-y-2">
                <input
                  type="date"
                  value={filters.custom_start || ''}
                  onChange={(e) => updateFilter('custom_start', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md
                           focus:ring-2 focus:ring-blue-500 text-sm"
                  placeholder="Start date"
                />
                <input
                  type="date"
                  value={filters.custom_end || ''}
                  onChange={(e) => updateFilter('custom_end', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md
                           focus:ring-2 focus:ring-blue-500 text-sm"
                  placeholder="End date"
                />
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2 border-t">
            <button
              onClick={clearAllFilters}
              className="flex-1 px-3 py-2 text-sm text-gray-700 bg-white border
                       border-gray-300 rounded-md hover:bg-gray-50
                       focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Clear All
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="flex-1 px-3 py-2 text-sm text-white bg-blue-600 rounded-md
                       hover:bg-blue-700 focus:outline-none focus:ring-2
                       focus:ring-blue-500 font-medium"
            >
              Apply
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
