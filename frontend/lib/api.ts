/**
 * API client for backend communication with JWT authentication.
 *
 * This module provides a centralized API client that handles:
 * - JWT token management
 * - Authentication headers
 * - Error handling
 * - Type-safe API calls
 */

import {
  Task,
  CreateTaskInput,
  UpdateTaskInput,
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

// API base URL from environment variable with runtime fallback
function getApiUrl(): string {
  // Try environment variable first (set at build time in Vercel)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Runtime detection for production
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;

    // If deployed on Vercel, use Railway backend
    if (hostname.includes('vercel.app')) {
      return 'https://todo-app-production-be56.up.railway.app';
    }
  }

  // Default to localhost for local development
  return 'http://localhost:8000';
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
  getTasks: (userId: string, status?: string): Promise<Task[]> => {
    const query = status && status !== 'all' ? `?status=${status}` : '';
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

  toggleTask: (userId: string, taskId: number): Promise<Task> =>
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
