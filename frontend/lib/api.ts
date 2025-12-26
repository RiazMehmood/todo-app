/**
 * API client for backend communication with JWT authentication.
 *
 * This module provides a centralized API client that handles:
 * - JWT token management
 * - Authentication headers
 * - Error handling
 * - Type-safe API calls
 *
 * Phase V Enhancement: Added support for advanced filtering, recurring tasks, and new task fields.
 */

import {
  Task,
  CreateTaskInput,
  UpdateTaskInput,
  TaskFilterParams,
  ToggleTaskResponse,
  SignupInput,
  LoginInput,
  AuthResponse,
  ApiError,
  UserPreferences,
  AIOptInRequest,
  AIPreferencesUpdate,
  ChatMessageInput,
  Message,
} from './types';

// API base URL - use empty string for production (Next.js rewrites handle proxying)
function getApiUrl(): string {
  // In production (Vercel), use empty string to leverage Next.js rewrites/proxy
  // This avoids Mixed Content issues (HTTPS frontend calling HTTP backend)
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;

    // Production deployments: use relative URLs (Next.js proxy handles backend call)
    if (hostname.includes('vercel.app') || hostname === 'todo.local' || hostname.includes('todo.local')) {
      return '';
    }
  }

  // Local development: point directly to backend
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

const API_URL = getApiUrl();

// Log the API URL being used (helps with debugging)
if (typeof window !== 'undefined') {
  console.log('🔗 API URL:', API_URL);
}

// Token storage key
const TOKEN_KEY = 'todo_auth_token';
const USER_KEY = 'todo_user';

/**
 * Store authentication token in localStorage.
 */
export function setAuthToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

/**
 * Get authentication token from localStorage.
 */
export function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

/**
 * Remove authentication token from localStorage.
 */
export function clearAuthToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

/**
 * Store user data in localStorage.
 */
export function setUser(user: any): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}

/**
 * Get user data from localStorage.
 */
export function getUser(): any | null {
  if (typeof window !== 'undefined') {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }
  return null;
}

/**
 * Generic API call function with JWT authentication.
 *
 * @param endpoint - API endpoint (e.g., "/api/user123/tasks")
 * @param options - Fetch options (method, body, headers, etc.)
 * @returns Promise with parsed JSON response
 * @throws Error if request fails
 */
export async function apiCall<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();

  // Build request options
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  };

  try {
    const response = await fetch(`${API_URL}${endpoint}`, config);

    // Handle 401 Unauthorized (token expired or invalid)
    if (response.status === 401) {
      clearAuthToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/login?error=session_expired';
      }
      throw new Error('Session expired. Please log in again.');
    }

    // Handle other errors
    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw new Error(error.detail || 'API request failed');
    }

    // Parse and return JSON response
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Network error. Please check your connection.');
  }
}

/**
 * API methods for specific endpoints.
 */
export const api = {
  // Authentication
  signup: (data: SignupInput): Promise<AuthResponse> =>
    apiCall('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: LoginInput): Promise<AuthResponse> =>
    apiCall('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Tasks
  /**
   * Get tasks with advanced filtering, search, and sorting (Phase V).
   *
   * @param userId - User ID
   * @param filters - Optional filters (status, priority, tags, search, due dates, sorting, pagination)
   * @returns Promise with array of tasks
   */
  getTasks: (userId: string, filters?: TaskFilterParams): Promise<Task[]> => {
    // Build query string from filters
    const params = new URLSearchParams();

    if (filters) {
      if (filters.status) params.append('status', filters.status);
      if (filters.priority) params.append('priority', filters.priority);
      if (filters.tags) params.append('tags', filters.tags);
      if (filters.search) params.append('search', filters.search);
      if (filters.due_date_before) params.append('due_date_before', filters.due_date_before);
      if (filters.due_date_after) params.append('due_date_after', filters.due_date_after);
      if (filters.is_recurring !== undefined) params.append('is_recurring', String(filters.is_recurring));
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      if (filters.sort_order) params.append('sort_order', filters.sort_order);
      if (filters.limit) params.append('limit', String(filters.limit));
      if (filters.offset) params.append('offset', String(filters.offset));
    }

    const query = params.toString() ? `?${params.toString()}` : '';
    return apiCall(`/api/${userId}/tasks${query}`);
  },

  getTask: (userId: string, taskId: number): Promise<Task> =>
    apiCall(`/api/${userId}/tasks/${taskId}`),

  createTask: (userId: string, data: CreateTaskInput): Promise<Task> =>
    apiCall(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateTask: (
    userId: string,
    taskId: number,
    data: UpdateTaskInput
  ): Promise<Task> =>
    apiCall(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteTask: (userId: string, taskId: number): Promise<{ message: string; id: number }> =>
    apiCall(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    }),

  /**
   * Toggle task completion status (Phase V).
   *
   * For recurring tasks, this will mark the current instance as complete
   * and create a new task instance for the next occurrence.
   *
   * @param userId - User ID
   * @param taskId - Task ID
   * @returns Promise with toggle response (includes next_task for recurring tasks)
   */
  toggleTask: (userId: string, taskId: number): Promise<ToggleTaskResponse> =>
    apiCall(`/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    }),

  // ========================================================================
  // Phase III: AI Chatbot Integration
  // ========================================================================

  // AI Preferences
  aiOptIn: (userId: string, data: AIOptInRequest): Promise<UserPreferences> =>
    apiCall(`/api/auth/users/${userId}/ai/opt-in`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  aiOptOut: (userId: string, deleteHistory: boolean = false): Promise<{ message: string }> =>
    apiCall(`/api/auth/users/${userId}/ai/opt-out?delete_history=${deleteHistory}`, {
      method: 'POST',
    }),

  getAIPreferences: (userId: string): Promise<UserPreferences> =>
    apiCall(`/api/auth/users/${userId}/ai/preferences`),

  updateAIPreferences: (userId: string, data: AIPreferencesUpdate): Promise<UserPreferences> =>
    apiCall(`/api/auth/users/${userId}/ai/preferences`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  // Chat
  sendChatMessage: (userId: string, message: string): Promise<{
    conversation_id: number;
    user_message_id: number;
    assistant_message_id: number;
    response: string;
    language?: string;
    related_task_id?: number;
  }> =>
    apiCall(`/api/${userId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message, stream: false }),
    }),

  getChatHistory: (userId: string): Promise<{
    conversation_id: number;
    messages: Message[];
  }> =>
    apiCall(`/api/${userId}/chat/history`),

  deleteChatHistory: (userId: string): Promise<{ message: string; messages_deleted: number }> =>
    apiCall(`/api/${userId}/chat/history`, {
      method: 'DELETE',
    }),
};
