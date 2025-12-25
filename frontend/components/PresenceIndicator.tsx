/**
 * PresenceIndicator Component - Real-time user presence display
 *
 * Implements: User Story 3 (Real-Time Collaboration) from intermediate-advanced-features.md
 * Protocol: specs/005-cloud-native-deployment/contracts/websocket-protocol.md
 */

'use client'

import { useState, useEffect } from 'react'
import { getWebSocketClient, PresenceUser } from '@/lib/websocket'

interface PresenceIndicatorProps {
  /** Current user ID */
  userId: string
  /** JWT token for WebSocket authentication */
  token: string
  /** Optional task ID to filter presence (show only users viewing/editing this task) */
  taskId?: string
  /** Show compact view (avatar only, no names) */
  compact?: boolean
}

export default function PresenceIndicator({
  userId,
  token,
  taskId,
  compact = false
}: PresenceIndicatorProps) {
  const [activeUsers, setActiveUsers] = useState<PresenceUser[]>([])
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    // Get WebSocket client
    const ws = getWebSocketClient(userId, token)

    // Handle presence updates
    const handlePresenceUpdate = (data: any) => {
      const users: PresenceUser[] = data.users || []

      // Filter by taskId if provided
      let filteredUsers = users
      if (taskId) {
        filteredUsers = users.filter(user => user.task_id === taskId)
      }

      // Exclude current user
      const otherUsers = filteredUsers.filter(user => user.user_id !== userId)

      setActiveUsers(otherUsers)
    }

    // Handle connection state changes
    const handleStateChange = (state: string) => {
      setIsConnected(state === 'connected')
    }

    // Register event handlers
    ws.on('presence_update', handlePresenceUpdate)
    ws.onStateChange(handleStateChange)

    // Connect if not already connected
    if (ws.getState() === 'disconnected') {
      ws.connect()
    } else {
      setIsConnected(ws.getState() === 'connected')
    }

    // Cleanup
    return () => {
      ws.off('presence_update', handlePresenceUpdate)
      ws.offStateChange(handleStateChange)
    }
  }, [userId, token, taskId])

  // Get user initials from username
  const getInitials = (username: string): string => {
    const parts = username.split(' ')
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
    }
    return username.substring(0, 2).toUpperCase()
  }

  // Get status color
  const getStatusColor = (status: PresenceUser['status']): string => {
    switch (status) {
      case 'editing':
        return 'bg-green-500'
      case 'viewing':
        return 'bg-blue-500'
      case 'idle':
        return 'bg-gray-400'
      default:
        return 'bg-gray-400'
    }
  }

  // Get status text
  const getStatusText = (status: PresenceUser['status']): string => {
    switch (status) {
      case 'editing':
        return 'Editing'
      case 'viewing':
        return 'Viewing'
      case 'idle':
        return 'Idle'
      default:
        return 'Unknown'
    }
  }

  // Format last seen time
  const formatLastSeen = (lastSeen: string): string => {
    const now = new Date()
    const lastSeenDate = new Date(lastSeen)
    const diffSeconds = Math.floor((now.getTime() - lastSeenDate.getTime()) / 1000)

    if (diffSeconds < 10) {
      return 'just now'
    } else if (diffSeconds < 60) {
      return `${diffSeconds}s ago`
    } else {
      const diffMinutes = Math.floor(diffSeconds / 60)
      return `${diffMinutes}m ago`
    }
  }

  // Don't render if no active users
  if (activeUsers.length === 0) {
    return null
  }

  // Compact view (mobile/small screens)
  if (compact) {
    return (
      <div className="flex items-center gap-1" role="list" aria-label="Active users">
        {/* User count */}
        <span className="text-xs text-gray-600 mr-1">
          {activeUsers.length} online
        </span>

        {/* User avatars (max 5, then +N) */}
        {activeUsers.slice(0, 5).map((user) => (
          <div
            key={user.user_id}
            className="relative group"
            role="listitem"
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold text-white ${getStatusColor(user.status)}`}
              aria-label={`${user.username} - ${getStatusText(user.status)}`}
            >
              {getInitials(user.username)}
            </div>

            {/* Tooltip */}
            <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 hidden group-hover:block z-50">
              <div className="bg-gray-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap">
                <div className="font-semibold">{user.username}</div>
                <div className="text-gray-300">{getStatusText(user.status)}</div>
                <div className="text-gray-400">{formatLastSeen(user.last_seen)}</div>
              </div>
              <div className="w-2 h-2 bg-gray-900 rotate-45 absolute top-full left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
            </div>
          </div>
        ))}

        {/* Overflow indicator */}
        {activeUsers.length > 5 && (
          <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-semibold text-gray-700">
            +{activeUsers.length - 5}
          </div>
        )}
      </div>
    )
  }

  // Full view (desktop)
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-900">
          Active Users
        </h3>
        <div className="flex items-center gap-2">
          {/* Connection indicator */}
          <div className="flex items-center gap-1">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-xs text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* User count */}
          <span className="text-xs text-gray-600">
            {activeUsers.length} online
          </span>
        </div>
      </div>

      {/* User list */}
      <div className="space-y-2" role="list" aria-label="Active users">
        {activeUsers.map((user) => (
          <div
            key={user.user_id}
            className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
            role="listitem"
          >
            {/* Avatar with status indicator */}
            <div className="relative">
              <div
                className="w-10 h-10 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-sm font-semibold"
                aria-label={user.username}
              >
                {getInitials(user.username)}
              </div>

              {/* Status indicator dot */}
              <div
                className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white ${getStatusColor(user.status)}`}
                aria-label={getStatusText(user.status)}
              ></div>
            </div>

            {/* User info */}
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900 truncate">
                {user.username}
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <span className={`font-medium ${
                  user.status === 'editing' ? 'text-green-600' :
                  user.status === 'viewing' ? 'text-blue-600' :
                  'text-gray-500'
                }`}>
                  {getStatusText(user.status)}
                </span>
                <span>•</span>
                <span>{formatLastSeen(user.last_seen)}</span>
              </div>
            </div>

            {/* Task indicator (if viewing/editing specific task) */}
            {user.task_id && (
              <div className="text-xs text-gray-500">
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
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Empty state (shouldn't show due to early return, but good practice) */}
      {activeUsers.length === 0 && (
        <div className="text-center py-4 text-sm text-gray-500">
          No other users online
        </div>
      )}
    </div>
  )
}
