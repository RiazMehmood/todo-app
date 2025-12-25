/**
 * NotificationToast Component - Real-time notification display
 *
 * Implements: User Story 3 (Real-Time Collaboration) from intermediate-advanced-features.md
 * Protocol: specs/005-cloud-native-deployment/contracts/websocket-protocol.md
 */

'use client'

import { useState, useEffect, useCallback } from 'react'
import { getWebSocketClient } from '@/lib/websocket'

export type NotificationType = 'success' | 'info' | 'warning' | 'error'

export interface Notification {
  id: string
  type: NotificationType
  title: string
  message: string
  action?: {
    label: string
    onClick: () => void
  }
  duration?: number // milliseconds, 0 = no auto-dismiss
}

interface NotificationToastProps {
  /** Current user ID */
  userId: string
  /** JWT token for WebSocket authentication */
  token: string
  /** Default duration in milliseconds (default: 5000) */
  defaultDuration?: number
}

export default function NotificationToast({
  userId,
  token,
  defaultDuration = 5000
}: NotificationToastProps) {
  const [notifications, setNotifications] = useState<Notification[]>([])

  useEffect(() => {
    // Get WebSocket client
    const ws = getWebSocketClient(userId, token)

    // Handle notification messages from WebSocket
    const handleNotification = (data: any) => {
      const notification: Notification = {
        id: `notif-${Date.now()}-${Math.random()}`,
        type: getNotificationType(data.action),
        title: data.title || 'Notification',
        message: data.message || '',
        duration: defaultDuration
      }

      addNotification(notification)
    }

    // Handle task events and convert to notifications
    const handleTaskCreated = (data: any) => {
      const notification: Notification = {
        id: `notif-${Date.now()}-${Math.random()}`,
        type: 'success',
        title: 'Task Created',
        message: `New task: ${data.task?.title || 'Untitled'}`,
        duration: defaultDuration
      }

      addNotification(notification)
    }

    const handleTaskUpdated = (data: any) => {
      const notification: Notification = {
        id: `notif-${Date.now()}-${Math.random()}`,
        type: 'info',
        title: 'Task Updated',
        message: `Task updated: ${data.task?.title || 'Untitled'}`,
        duration: defaultDuration
      }

      addNotification(notification)
    }

    const handleTaskDeleted = (data: any) => {
      const notification: Notification = {
        id: `notif-${Date.now()}-${Math.random()}`,
        type: 'warning',
        title: 'Task Deleted',
        message: 'A task was deleted',
        duration: defaultDuration
      }

      addNotification(notification)
    }

    // Register event handlers
    ws.on('notification', handleNotification)
    ws.on('task_created', handleTaskCreated)
    ws.on('task_updated', handleTaskUpdated)
    ws.on('task_deleted', handleTaskDeleted)

    // Connect if not already connected
    if (ws.getState() === 'disconnected') {
      ws.connect()
    }

    // Cleanup
    return () => {
      ws.off('notification', handleNotification)
      ws.off('task_created', handleTaskCreated)
      ws.off('task_updated', handleTaskUpdated)
      ws.off('task_deleted', handleTaskDeleted)
    }
  }, [userId, token, defaultDuration])

  const addNotification = useCallback((notification: Notification) => {
    setNotifications(prev => [...prev, notification])

    // Auto-dismiss after duration
    if (notification.duration && notification.duration > 0) {
      setTimeout(() => {
        removeNotification(notification.id)
      }, notification.duration)
    }
  }, [])

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const getNotificationType = (action?: string): NotificationType => {
    if (!action) return 'info'

    if (action.includes('completed') || action.includes('success')) {
      return 'success'
    } else if (action.includes('error') || action.includes('failed')) {
      return 'error'
    } else if (action.includes('warning') || action.includes('deleted')) {
      return 'warning'
    }

    return 'info'
  }

  // Get notification styles based on type
  const getNotificationStyles = (type: NotificationType) => {
    switch (type) {
      case 'success':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          icon: 'text-green-600',
          iconBg: 'bg-green-100',
          title: 'text-green-900',
          message: 'text-green-700'
        }
      case 'error':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: 'text-red-600',
          iconBg: 'bg-red-100',
          title: 'text-red-900',
          message: 'text-red-700'
        }
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: 'text-yellow-600',
          iconBg: 'bg-yellow-100',
          title: 'text-yellow-900',
          message: 'text-yellow-700'
        }
      case 'info':
      default:
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          icon: 'text-blue-600',
          iconBg: 'bg-blue-100',
          title: 'text-blue-900',
          message: 'text-blue-700'
        }
    }
  }

  // Get icon for notification type
  const getIcon = (type: NotificationType) => {
    switch (type) {
      case 'success':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        )
      case 'error':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        )
      case 'warning':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )
      case 'info':
      default:
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
    }
  }

  if (notifications.length === 0) {
    return null
  }

  return (
    <div
      className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none max-w-sm w-full"
      role="region"
      aria-label="Notifications"
      aria-live="polite"
    >
      {notifications.map((notification) => {
        const styles = getNotificationStyles(notification.type)

        return (
          <div
            key={notification.id}
            className={`${styles.bg} ${styles.border} border rounded-lg shadow-lg p-4 pointer-events-auto animate-slide-in-right`}
            role="alert"
            aria-atomic="true"
          >
            <div className="flex items-start gap-3">
              {/* Icon */}
              <div className={`${styles.iconBg} ${styles.icon} rounded-full p-2 flex-shrink-0`}>
                {getIcon(notification.type)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <h4 className={`text-sm font-semibold ${styles.title} mb-1`}>
                  {notification.title}
                </h4>
                <p className={`text-sm ${styles.message}`}>
                  {notification.message}
                </p>

                {/* Action button */}
                {notification.action && (
                  <button
                    onClick={notification.action.onClick}
                    className={`mt-2 text-sm font-medium ${styles.icon} hover:underline`}
                  >
                    {notification.action.label}
                  </button>
                )}
              </div>

              {/* Dismiss button */}
              <button
                onClick={() => removeNotification(notification.id)}
                className="text-gray-400 hover:text-gray-600 flex-shrink-0"
                aria-label="Dismiss notification"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )
      })}

      {/* CSS Animation */}
      <style jsx>{`
        @keyframes slide-in-right {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }

        .animate-slide-in-right {
          animation: slide-in-right 0.3s ease-out;
        }
      `}</style>
    </div>
  )
}
