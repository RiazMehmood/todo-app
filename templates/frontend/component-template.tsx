/**
 * React Component Template - Next.js 16+ App Router Pattern
 *
 * This template demonstrates the pattern for creating React components
 * with TypeScript in Next.js 16+ using the App Router.
 *
 * Usage:
 * 1. Copy this template
 * 2. Rename ComponentTemplate to your component name
 * 3. Define props interface
 * 4. Implement component logic
 * 5. Add styling with Tailwind CSS
 *
 * Example from Phase II & III:
 * - TaskList.tsx, TaskForm.tsx, ChatInterface.tsx, AISettingsPanel.tsx
 */

'use client';  // Add this for client components (useState, useEffect, event handlers)

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// ========================================
// 1. Type Definitions
// ========================================

/**
 * Props interface for ComponentTemplate.
 */
interface ComponentTemplateProps {
  /**
   * Required prop description
   */
  requiredProp: string;

  /**
   * Optional prop description
   */
  optionalProp?: string;

  /**
   * Callback function when action occurs
   */
  onAction?: (data: any) => void;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Internal state interface
 */
interface ComponentState {
  loading: boolean;
  error: string | null;
  data: any | null;
}

// ========================================
// 2. Component Definition
// ========================================

/**
 * ComponentTemplate - Brief description of what this component does.
 *
 * @param props - Component props
 * @returns JSX element
 *
 * @example
 * ```tsx
 * <ComponentTemplate
 *   requiredProp="value"
 *   optionalProp="optional value"
 *   onAction={(data) => console.log(data)}
 * />
 * ```
 */
export default function ComponentTemplate({
  requiredProp,
  optionalProp = 'default value',
  onAction,
  className = ''
}: ComponentTemplateProps) {
  // ========================================
  // 3. Hooks & State
  // ========================================

  const router = useRouter();

  // State management
  const [state, setState] = useState<ComponentState>({
    loading: false,
    error: null,
    data: null
  });

  // Local state for form/input
  const [inputValue, setInputValue] = useState('');

  // ========================================
  // 4. Effects
  // ========================================

  useEffect(() => {
    // Fetch data or initialize on mount
    const fetchData = async () => {
      setState(prev => ({ ...prev, loading: true }));

      try {
        // TODO: Replace with actual API call
        // const data = await fetchSomeData();
        // setState({ loading: false, error: null, data });

        console.log('Component mounted with', requiredProp);
      } catch (error) {
        setState({
          loading: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          data: null
        });
      }
    };

    fetchData();
  }, [requiredProp]); // Re-run when requiredProp changes

  // ========================================
  // 5. Event Handlers
  // ========================================

  /**
   * Handle form submission or action
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim()) {
      setState(prev => ({ ...prev, error: 'Input cannot be empty' }));
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      // TODO: Replace with actual API call
      // const result = await performAction(inputValue);

      // Call parent callback if provided
      onAction?.(inputValue);

      // Clear input
      setInputValue('');

      // Update state
      setState({
        loading: false,
        error: null,
        data: 'Success'
      });
    } catch (error) {
      setState({
        loading: false,
        error: error instanceof Error ? error.message : 'Operation failed',
        data: null
      });
    }
  };

  /**
   * Handle input change
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
    // Clear error when user types
    if (state.error) {
      setState(prev => ({ ...prev, error: null }));
    }
  };

  /**
   * Handle cancel/reset
   */
  const handleCancel = () => {
    setInputValue('');
    setState({ loading: false, error: null, data: null });
  };

  // ========================================
  // 6. Render Helpers
  // ========================================

  /**
   * Render loading state
   */
  const renderLoading = () => (
    <div className="flex items-center justify-center p-4">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <span className="ml-3 text-gray-600">Loading...</span>
    </div>
  );

  /**
   * Render error state
   */
  const renderError = () => (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <p className="text-red-800 text-sm">{state.error}</p>
      <button
        onClick={handleCancel}
        className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
      >
        Dismiss
      </button>
    </div>
  );

  /**
   * Render empty state
   */
  const renderEmpty = () => (
    <div className="text-center py-8 text-gray-500">
      <p>No data available</p>
      <p className="text-sm mt-2">Try adding something first</p>
    </div>
  );

  // ========================================
  // 7. Main Render
  // ========================================

  return (
    <div className={`component-template ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Component Title
        </h2>
        <p className="text-gray-600 mt-1">
          Component description or subtitle
        </p>
      </div>

      {/* Error Display */}
      {state.error && renderError()}

      {/* Loading State */}
      {state.loading && renderLoading()}

      {/* Main Content */}
      {!state.loading && (
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Input Field */}
          <div>
            <label
              htmlFor="input-field"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Input Label
            </label>
            <input
              id="input-field"
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              placeholder="Enter something..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={state.loading}
            />
            <p className="text-sm text-gray-500 mt-1">
              Helper text or instructions
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={state.loading || !inputValue.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {state.loading ? 'Processing...' : 'Submit'}
            </button>
            <button
              type="button"
              onClick={handleCancel}
              disabled={state.loading}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Data Display */}
      {state.data && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800">
            Success! Data: {JSON.stringify(state.data)}
          </p>
        </div>
      )}

      {/* Empty State */}
      {!state.loading && !state.data && !state.error && renderEmpty()}

      {/* Optional Prop Display */}
      {optionalProp && (
        <p className="mt-4 text-sm text-gray-500">
          Optional: {optionalProp}
        </p>
      )}
    </div>
  );
}

// ========================================
// Example: Real Component from Phase II
// ========================================

/**
 * TaskItem component - Display a single task
 */
interface TaskItemProps {
  task: {
    id: number;
    title: string;
    completed: boolean;
  };
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
}

export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <div className="flex items-center gap-3 p-4 bg-white border rounded-lg hover:shadow-md transition-shadow">
      {/* Checkbox */}
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
        className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
      />

      {/* Title */}
      <span className={`flex-1 ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
        {task.title}
      </span>

      {/* Delete Button */}
      <button
        onClick={() => onDelete(task.id)}
        className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
        aria-label="Delete task"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  );
}

// ========================================
// Best Practices
// ========================================

// 1. File Organization:
//    - One main component per file
//    - Related helper components in same file
//    - Move to separate files if reused elsewhere

// 2. TypeScript:
//    - Define props interface
//    - Type all state variables
//    - Type event handlers
//    - Avoid 'any' type when possible

// 3. State Management:
//    - Use useState for local state
//    - Use useEffect for side effects
//    - Keep state minimal and derived
//    - Lift state up when needed

// 4. Accessibility:
//    - Use semantic HTML
//    - Add aria-labels for buttons
//    - Support keyboard navigation
//    - Test with screen readers

// 5. Performance:
//    - Use 'use client' only when needed
//    - Memoize expensive calculations (useMemo)
//    - Prevent unnecessary re-renders (useCallback)
//    - Lazy load heavy components

// 6. Error Handling:
//    - Always catch async errors
//    - Display user-friendly error messages
//    - Provide recovery actions
//    - Log errors for debugging

// 7. Styling:
//    - Use Tailwind CSS classes
//    - Follow existing design system
//    - Ensure responsive design
//    - Test on different screen sizes

// 8. Testing:
//    - Test user interactions
//    - Test error states
//    - Test loading states
//    - Test with different props
