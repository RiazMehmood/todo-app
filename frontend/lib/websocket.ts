/**
 * WebSocket Client - Real-time communication with backend
 *
 * Implements: WebSocket protocol from specs/005-cloud-native-deployment/contracts/websocket-protocol.md
 *
 * Features:
 * - Automatic reconnection with exponential backoff (1s → 30s)
 * - Heartbeat sending every 10 seconds
 * - Event handlers for all message types
 * - Connection state management
 * - Type-safe message handling
 */

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'reconnecting'

export type MessageType =
  | 'welcome'
  | 'task_created'
  | 'task_updated'
  | 'task_deleted'
  | 'presence_update'
  | 'notification'
  | 'error'

export type UserStatus = 'viewing' | 'editing' | 'idle'

export interface WebSocketMessage {
  type: MessageType
  [key: string]: any
}

export interface Task {
  id: string
  user_id: string
  title: string
  description?: string
  status: 'pending' | 'in_progress' | 'completed'
  priority: 'low' | 'medium' | 'high'
  tags?: string[]
  created_at: string
  updated_at: string
  due_date?: string
}

export interface PresenceUser {
  user_id: string
  username: string
  task_id: string | null
  status: UserStatus
  last_seen: string
}

export type MessageHandler = (data: any) => void

export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private token: string
  private userId: string

  // Connection state
  private state: ConnectionState = 'disconnected'
  private sessionId: string | null = null

  // Reconnection
  private reconnectAttempts = 0
  private maxReconnectDelay = 30000 // 30 seconds
  private reconnectTimer: NodeJS.Timeout | null = null

  // Heartbeat
  private heartbeatInterval: NodeJS.Timeout | null = null
  private heartbeatDelay = 10000 // 10 seconds
  private currentTaskId: string | null = null
  private currentStatus: UserStatus = 'viewing'

  // Event handlers
  private messageHandlers: Map<MessageType, Set<MessageHandler>> = new Map()
  private stateChangeHandlers: Set<(state: ConnectionState) => void> = new Set()

  constructor(userId: string, token: string, wsUrl?: string) {
    this.userId = userId
    this.token = token

    // Build WebSocket URL (use env var or default)
    const baseUrl = wsUrl || process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    this.url = `${baseUrl}/api/${userId}/ws?token=${token}`
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.state === 'connected' || this.state === 'connecting') {
      console.log('WebSocket already connected or connecting')
      return
    }

    console.log('🔌 Connecting to WebSocket...')
    this.setState('connecting')

    try {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = this.handleOpen.bind(this)
      this.ws.onmessage = this.handleMessage.bind(this)
      this.ws.onerror = this.handleError.bind(this)
      this.ws.onclose = this.handleClose.bind(this)
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      this.scheduleReconnect()
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    console.log('🔌 Disconnecting WebSocket...')

    // Clear timers
    this.stopHeartbeat()
    this.cancelReconnect()

    // Close connection
    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting')
      this.ws = null
    }

    this.setState('disconnected')
    this.sessionId = null
    this.reconnectAttempts = 0
  }

  /**
   * Send message to server
   */
  send(message: any): void {
    if (this.state !== 'connected' || !this.ws) {
      console.warn('Cannot send message: WebSocket not connected')
      return
    }

    try {
      this.ws.send(JSON.stringify(message))
    } catch (error) {
      console.error('Failed to send WebSocket message:', error)
    }
  }

  /**
   * Update current presence (task being viewed/edited)
   */
  updatePresence(taskId: string | null, status: UserStatus): void {
    this.currentTaskId = taskId
    this.currentStatus = status

    // Send heartbeat immediately with new presence
    this.sendHeartbeat()
  }

  /**
   * Notify server that user started editing a task
   */
  startEditingTask(taskId: string): void {
    this.send({
      type: 'task_edit_start',
      task_id: taskId
    })
    this.updatePresence(taskId, 'editing')
  }

  /**
   * Notify server that user stopped editing a task
   */
  stopEditingTask(taskId: string): void {
    this.send({
      type: 'task_edit_end',
      task_id: taskId
    })
    this.updatePresence(taskId, 'viewing')
  }

  /**
   * Register event handler for specific message type
   */
  on(messageType: MessageType, handler: MessageHandler): void {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, new Set())
    }
    this.messageHandlers.get(messageType)!.add(handler)
  }

  /**
   * Unregister event handler
   */
  off(messageType: MessageType, handler: MessageHandler): void {
    const handlers = this.messageHandlers.get(messageType)
    if (handlers) {
      handlers.delete(handler)
    }
  }

  /**
   * Register connection state change handler
   */
  onStateChange(handler: (state: ConnectionState) => void): void {
    this.stateChangeHandlers.add(handler)
  }

  /**
   * Unregister connection state change handler
   */
  offStateChange(handler: (state: ConnectionState) => void): void {
    this.stateChangeHandlers.delete(handler)
  }

  /**
   * Get current connection state
   */
  getState(): ConnectionState {
    return this.state
  }

  /**
   * Get session ID (available after connection)
   */
  getSessionId(): string | null {
    return this.sessionId
  }

  // Private methods

  private handleOpen(): void {
    console.log('✅ WebSocket connected')
    this.setState('connected')
    this.reconnectAttempts = 0

    // Start heartbeat
    this.startHeartbeat()
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data)
      const messageType = message.type

      // Handle welcome message
      if (messageType === 'welcome') {
        this.sessionId = message.session_id
        console.log(`📝 Session ID: ${this.sessionId}`)
      }

      // Dispatch to registered handlers
      const handlers = this.messageHandlers.get(messageType)
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message)
          } catch (error) {
            console.error(`Error in ${messageType} handler:`, error)
          }
        })
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error)
    }
  }

  private handleError(event: Event): void {
    console.error('❌ WebSocket error:', event)
  }

  private handleClose(event: CloseEvent): void {
    console.log(`🔌 WebSocket closed: code=${event.code}, reason=${event.reason}`)

    this.stopHeartbeat()
    this.ws = null
    this.sessionId = null

    // Reconnect unless it was a normal closure
    if (event.code !== 1000) {
      this.scheduleReconnect()
    } else {
      this.setState('disconnected')
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return // Already scheduled
    }

    this.setState('reconnecting')

    // Calculate backoff delay: 1s, 2s, 4s, 8s, 16s, max 30s
    const delay = Math.min(
      1000 * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    )

    console.log(`🔄 Reconnecting in ${delay / 1000}s (attempt ${this.reconnectAttempts + 1})`)

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      this.reconnectAttempts++
      this.connect()
    }, delay)
  }

  private cancelReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat()

    // Send initial heartbeat
    this.sendHeartbeat()

    // Schedule periodic heartbeats (every 10 seconds)
    this.heartbeatInterval = setInterval(() => {
      this.sendHeartbeat()
    }, this.heartbeatDelay)
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  private sendHeartbeat(): void {
    this.send({
      type: 'heartbeat',
      task_id: this.currentTaskId,
      status: this.currentStatus
    })
  }

  private setState(state: ConnectionState): void {
    if (this.state !== state) {
      this.state = state
      console.log(`📡 WebSocket state: ${state}`)

      // Notify state change handlers
      this.stateChangeHandlers.forEach(handler => {
        try {
          handler(state)
        } catch (error) {
          console.error('Error in state change handler:', error)
        }
      })
    }
  }
}

/**
 * Create and manage WebSocket client instance (singleton pattern)
 */
let wsClient: WebSocketClient | null = null

export function getWebSocketClient(userId: string, token: string): WebSocketClient {
  if (!wsClient || wsClient.getState() === 'disconnected') {
    wsClient = new WebSocketClient(userId, token)
  }
  return wsClient
}

export function disconnectWebSocket(): void {
  if (wsClient) {
    wsClient.disconnect()
    wsClient = null
  }
}
