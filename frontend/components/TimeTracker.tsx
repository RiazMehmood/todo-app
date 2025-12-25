/**
 * TimeTracker Component - Start/stop timer for task time tracking
 *
 * Implements: User Story 4 (Analytics and Reporting - Time Tracking) from intermediate-advanced-features.md
 * Contract: specs/005-cloud-native-deployment/contracts/analytics-api.yaml
 *
 * Features:
 * - FR-030: Start/stop timer for tracking time spent on tasks
 * - FR-038: Timer persistence across page refreshes
 * - FR-075: Create and update time entries via API
 * - Display elapsed time in real-time
 * - Save work description when stopping timer
 */

'use client'

import { useState, useEffect, useCallback } from 'react'

// ============================================================================
// TypeScript Interfaces (from analytics-api.yaml)
// ============================================================================

interface TimeEntry {
  id: string
  task_id: string
  user_id: string
  started_at: string
  ended_at: string | null
  elapsed_seconds: number | null
  description: string | null
  created_at: string
}

interface TimeTrackerProps {
  /** Task ID to track time for */
  taskId: string
  /** User ID (from auth context) */
  userId: string
  /** Callback when timer state changes */
  onTimerChange?: (isRunning: boolean, elapsed: number) => void
  /** Optional existing active time entry */
  activeEntry?: TimeEntry | null
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Format seconds into human-readable time (HH:MM:SS)
 */
function formatElapsedTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  return [hours, minutes, secs]
    .map(v => v.toString().padStart(2, '0'))
    .join(':')
}

/**
 * Calculate elapsed seconds between two timestamps
 */
function calculateElapsed(startTime: string, endTime?: string): number {
  const start = new Date(startTime).getTime()
  const end = endTime ? new Date(endTime).getTime() : Date.now()
  return Math.floor((end - start) / 1000)
}

// ============================================================================
// Main Component
// ============================================================================

export default function TimeTracker({
  taskId,
  userId,
  onTimerChange,
  activeEntry = null
}: TimeTrackerProps) {
  // State management
  const [isRunning, setIsRunning] = useState(false)
  const [currentEntry, setCurrentEntry] = useState<TimeEntry | null>(activeEntry)
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  // Load active timer from localStorage on mount (FR-038: persistence)
  useEffect(() => {
    const savedEntry = localStorage.getItem(`timer_${taskId}`)
    if (savedEntry) {
      try {
        const entry = JSON.parse(savedEntry) as TimeEntry
        setCurrentEntry(entry)
        setIsRunning(true)
        setElapsedSeconds(calculateElapsed(entry.started_at))
      } catch (err) {
        console.error('Failed to restore timer from localStorage:', err)
        localStorage.removeItem(`timer_${taskId}`)
      }
    } else if (activeEntry) {
      setCurrentEntry(activeEntry)
      setIsRunning(true)
      setElapsedSeconds(calculateElapsed(activeEntry.started_at))
    }
  }, [taskId, activeEntry])

  // Update elapsed time every second when timer is running
  useEffect(() => {
    if (!isRunning || !currentEntry) return

    const interval = setInterval(() => {
      const elapsed = calculateElapsed(currentEntry.started_at)
      setElapsedSeconds(elapsed)

      // Notify parent component
      onTimerChange?.(true, elapsed)
    }, 1000)

    return () => clearInterval(interval)
  }, [isRunning, currentEntry, onTimerChange])

  /**
   * Start timer - Create new time entry
   * Implements: POST /api/{user_id}/time-entries
   */
  const startTimer = useCallback(async () => {
    setError(null)
    setIsSaving(true)

    try {
      const response = await fetch(
        `http://localhost:8000/api/${userId}/time-entries`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            task_id: taskId,
            started_at: new Date().toISOString(),
            description: null
          })
        }
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to start timer')
      }

      const entry: TimeEntry = await response.json()
      setCurrentEntry(entry)
      setIsRunning(true)
      setElapsedSeconds(0)

      // Save to localStorage for persistence (FR-038)
      localStorage.setItem(`timer_${taskId}`, JSON.stringify(entry))

      onTimerChange?.(true, 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start timer')
      console.error('Start timer error:', err)
    } finally {
      setIsSaving(false)
    }
  }, [taskId, userId, onTimerChange])

  /**
   * Stop timer - Update time entry with end time
   * Implements: PATCH /api/{user_id}/time-entries/{entry_id}
   */
  const stopTimer = useCallback(async () => {
    if (!currentEntry) return

    setError(null)
    setIsSaving(true)

    try {
      const response = await fetch(
        `http://localhost:8000/api/${userId}/time-entries/${currentEntry.id}`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            ended_at: new Date().toISOString(),
            description: description.trim() || null
          })
        }
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to stop timer')
      }

      const updatedEntry: TimeEntry = await response.json()

      setIsRunning(false)
      setCurrentEntry(null)
      setDescription('')

      // Clear localStorage
      localStorage.removeItem(`timer_${taskId}`)

      onTimerChange?.(false, updatedEntry.elapsed_seconds || 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop timer')
      console.error('Stop timer error:', err)
    } finally {
      setIsSaving(false)
    }
  }, [currentEntry, userId, taskId, description, onTimerChange])

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">Time Tracker</h3>
        {isRunning && (
          <span className="flex items-center gap-1 text-xs text-green-600">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            Recording
          </span>
        )}
      </div>

      {/* Elapsed Time Display */}
      <div className="bg-gray-50 rounded-lg p-4 mb-4 text-center">
        <div
          className="text-4xl font-mono font-bold text-gray-900"
          aria-live="polite"
          aria-label="Elapsed time"
        >
          {formatElapsedTime(elapsedSeconds)}
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {isRunning ? 'Timer running' : 'Timer stopped'}
        </p>
      </div>

      {/* Work Description Input (shown when timer is running) */}
      {isRunning && (
        <div className="mb-4">
          <label
            htmlFor="work-description"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            What are you working on? (optional)
          </label>
          <textarea
            id="work-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g., Implementing search feature..."
            maxLength={500}
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />
          <p className="text-xs text-gray-500 mt-1">
            {description.length}/500 characters
          </p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Control Buttons */}
      <div className="flex gap-2">
        {!isRunning ? (
          <button
            onClick={startTimer}
            disabled={isSaving}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            aria-label="Start timer"
          >
            {isSaving ? 'Starting...' : '▶ Start Timer'}
          </button>
        ) : (
          <button
            onClick={stopTimer}
            disabled={isSaving}
            className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            aria-label="Stop timer"
          >
            {isSaving ? 'Stopping...' : '⏹ Stop Timer'}
          </button>
        )}
      </div>

      {/* Timer Info */}
      {currentEntry && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Started: {new Date(currentEntry.started_at).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  )
}
