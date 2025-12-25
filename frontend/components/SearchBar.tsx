'use client';

/**
 * SearchBar Component
 *
 * Advanced search input with autocomplete for tags and search history.
 * Supports full-text search with boolean operators.
 */

import { useState, useEffect, useRef } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface SearchBarProps {
  onSearch: (query: string) => void;
  userId: string;
  placeholder?: string;
  autoFocus?: boolean;
}

export function SearchBar({
  onSearch,
  userId,
  placeholder = "Search tasks... (try: urgent AND meeting, project OR task)",
  autoFocus = false
}: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Fetch tag suggestions when user types
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.length < 2) {
        setSuggestions([]);
        return;
      }

      try {
        // Get the last word being typed for tag suggestions
        const words = query.split(/\s+/);
        const lastWord = words[words.length - 1];

        if (lastWord.length < 2) {
          setSuggestions([]);
          return;
        }

        const response = await fetch(
          `/api/${userId}/search/suggestions?prefix=${encodeURIComponent(lastWord)}&type=tags`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setSuggestions(data.suggestions || []);
        }
      } catch (error) {
        console.error('Failed to fetch suggestions:', error);
        setSuggestions([]);
      }
    };

    const debounceTimer = setTimeout(fetchSuggestions, 300);

    return () => clearTimeout(debounceTimer);
  }, [query, userId]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
      setShowSuggestions(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) =>
        prev < suggestions.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) =>
        prev > 0 ? prev - 1 : suggestions.length - 1
      );
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault();
      applySuggestion(suggestions[selectedIndex]);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  const applySuggestion = (suggestion: string) => {
    const words = query.split(/\s+/);
    words[words.length - 1] = suggestion;
    const newQuery = words.join(' ') + ' ';
    setQuery(newQuery);
    setShowSuggestions(false);
    setSelectedIndex(-1);
    inputRef.current?.focus();
  };

  return (
    <div className="relative w-full">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>

          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setShowSuggestions(true);
              setSelectedIndex(-1);
            }}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => {
              // Delay hiding suggestions to allow click
              setTimeout(() => setShowSuggestions(false), 200);
            }}
            placeholder={placeholder}
            autoFocus={autoFocus}
            className="block w-full pl-10 pr-20 py-3 border border-gray-300 rounded-lg
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                     text-gray-900 placeholder-gray-500
                     transition-colors duration-200"
          />

          <div className="absolute inset-y-0 right-0 flex items-center pr-2">
            <button
              type="submit"
              className="px-4 py-1.5 bg-blue-600 text-white rounded-md
                       hover:bg-blue-700 focus:outline-none focus:ring-2
                       focus:ring-blue-500 focus:ring-offset-2
                       transition-colors duration-200
                       text-sm font-medium"
            >
              Search
            </button>
          </div>
        </div>
      </form>

      {/* Suggestions Dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-10 w-full mt-1 bg-white border border-gray-300
                   rounded-lg shadow-lg max-h-60 overflow-y-auto"
        >
          <div className="px-3 py-2 text-xs text-gray-500 font-medium border-b">
            Tag Suggestions
          </div>

          {suggestions.map((suggestion, index) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => applySuggestion(suggestion)}
              className={`w-full text-left px-4 py-2 hover:bg-gray-100
                        transition-colors duration-150
                        ${index === selectedIndex ? 'bg-blue-50' : ''}`}
            >
              <span className="text-sm text-gray-900">{suggestion}</span>
            </button>
          ))}
        </div>
      )}

      {/* Search Hints */}
      <div className="mt-2 text-xs text-gray-500">
        <span className="font-medium">Search tips:</span>
        {' '}Use <code className="px-1 bg-gray-100 rounded">AND</code>, <code className="px-1 bg-gray-100 rounded">OR</code>, <code className="px-1 bg-gray-100 rounded">NOT</code> for advanced queries
      </div>
    </div>
  );
}
