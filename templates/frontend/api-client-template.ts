/**
 * API Client Template - Frontend API Communication Pattern
 *
 * This template demonstrates the pattern for making API calls from the
 * Next.js frontend to the FastAPI backend with authentication.
 *
 * Usage:
 * 1. Copy this template to lib/api.ts
 * 2. Define TypeScript types for requests/responses
 * 3. Implement API functions using the pattern
 * 4. Handle authentication and errors consistently
 * 5. Use these functions in components
 *
 * Example from Phase II & III:
 * - lib/api.ts with task operations and chat operations
 */

// ========================================
// 1. Configuration
// ========================================

/**
 * Base API URL from environment variable
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * API endpoints
 */
const ENDPOINTS = {
  // Authentication
  login: '/api/auth/login',
  signup: '/api/auth/signup',

  // Resources (replace with your resources)
  entities: '/api/entities',
  entityById: (id: number) => `/api/entities/${id}`,

  // User-specific resources
  userEntities: (userId: string) => `/api/users/${userId}/entities`,
} as const;

// ========================================
// 2. Type Definitions
// ========================================

/**
 * API Error response
 */
export interface ApiError {
  detail: string;
  status?: number;
}

/**
 * Entity type (example - replace with your types)
 */
export interface Entity {
  id: number;
  user_id: string;
  required_field: string;
  optional_field?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Create entity request
 */
export interface CreateEntityRequest {
  required_field: string;
  optional_field?: string;
}

/**
 * Update entity request
 */
export interface UpdateEntityRequest {
  required_field?: string;
  optional_field?: string;
}

/**
 * List entities response
 */
export interface ListEntitiesResponse {
  entities: Entity[];
  total: number;
  limit: number;
  offset: number;
}

// ========================================
// 3. Helper Functions
// ========================================

/**
 * Get authentication token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

/**
 * Set authentication token in localStorage
 */
export function setAuthToken(token: string): void {
  localStorage.setItem('auth_token', token);
}

/**
 * Clear authentication token
 */
export function clearAuthToken(): void {
  localStorage.removeItem('auth_token');
}

/**
 * Build headers for API requests
 */
function buildHeaders(includeAuth: boolean = true): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (includeAuth) {
    const token = getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  return headers;
}

/**
 * Handle API errors
 */
function handleApiError(error: any): never {
  // Network error
  if (!error.response) {
    throw new Error('Network error: Please check your connection');
  }

  // HTTP error with detail
  if (error.detail) {
    throw new Error(error.detail);
  }

  // Generic error
  throw new Error('An unexpected error occurred');
}

/**
 * Make API request with error handling
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        ...buildHeaders(true),
        ...options.headers,
      },
    });

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    // Parse JSON response
    const data = await response.json();

    // Handle error responses
    if (!response.ok) {
      throw {
        response,
        detail: data.detail || `HTTP ${response.status}`,
        status: response.status,
      };
    }

    return data as T;
  } catch (error) {
    return handleApiError(error);
  }
}

// ========================================
// 4. Authentication API Functions
// ========================================

/**
 * Login user
 */
export async function login(
  email: string,
  password: string
): Promise<{ token: string; user: any }> {
  const response = await apiRequest<{ token: string; user: any }>(
    ENDPOINTS.login,
    {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }
  );

  // Save token
  setAuthToken(response.token);

  return response;
}

/**
 * Signup new user
 */
export async function signup(
  email: string,
  password: string,
  name: string
): Promise<{ token: string; user: any }> {
  const response = await apiRequest<{ token: string; user: any }>(
    ENDPOINTS.signup,
    {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    }
  );

  // Save token
  setAuthToken(response.token);

  return response;
}

/**
 * Logout user
 */
export function logout(): void {
  clearAuthToken();
  // Optionally redirect to login page
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

// ========================================
// 5. CRUD API Functions (Template)
// ========================================

/**
 * Create a new entity
 */
export async function createEntity(
  data: CreateEntityRequest
): Promise<Entity> {
  return apiRequest<Entity>(ENDPOINTS.entities, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Get entity by ID
 */
export async function getEntityById(id: number): Promise<Entity> {
  return apiRequest<Entity>(ENDPOINTS.entityById(id), {
    method: 'GET',
  });
}

/**
 * List entities with optional filtering
 */
export async function listEntities(params?: {
  filter_field?: string;
  limit?: number;
  offset?: number;
}): Promise<ListEntitiesResponse> {
  // Build query string
  const queryParams = new URLSearchParams();
  if (params?.filter_field) queryParams.set('filter_field', params.filter_field);
  if (params?.limit) queryParams.set('limit', params.limit.toString());
  if (params?.offset) queryParams.set('offset', params.offset.toString());

  const queryString = queryParams.toString();
  const endpoint = `${ENDPOINTS.entities}${queryString ? `?${queryString}` : ''}`;

  return apiRequest<ListEntitiesResponse>(endpoint, {
    method: 'GET',
  });
}

/**
 * Update entity
 */
export async function updateEntity(
  id: number,
  updates: UpdateEntityRequest
): Promise<Entity> {
  return apiRequest<Entity>(ENDPOINTS.entityById(id), {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

/**
 * Delete entity
 */
export async function deleteEntity(id: number): Promise<void> {
  await apiRequest<void>(ENDPOINTS.entityById(id), {
    method: 'DELETE',
  });
}

// ========================================
// 6. Example: Real API Functions from Phase III
// ========================================

/**
 * Chat message request
 */
export interface SendChatMessageRequest {
  conversation_id?: number;
  message: string;
}

/**
 * Chat message response
 */
export interface SendChatMessageResponse {
  conversation_id: number;
  response: string;
  tool_calls: any[];
}

/**
 * Send chat message to AI (Hackathon required endpoint)
 */
export async function sendChatMessage(
  userId: string,
  request: SendChatMessageRequest
): Promise<SendChatMessageResponse> {
  return apiRequest<SendChatMessageResponse>(
    `/api/${userId}/chat`,
    {
      method: 'POST',
      body: JSON.stringify(request),
    }
  );
}

/**
 * Get chat history
 */
export async function getChatHistory(
  userId: string,
  params?: {
    limit?: number;
    offset?: number;
  }
): Promise<{ messages: any[]; total: number; has_more: boolean }> {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.set('limit', params.limit.toString());
  if (params?.offset) queryParams.set('offset', params.offset.toString());

  const queryString = queryParams.toString();
  const endpoint = `/api/users/${userId}/chat/messages${queryString ? `?${queryString}` : ''}`;

  return apiRequest(endpoint, { method: 'GET' });
}

/**
 * AI opt-in
 */
export async function optInToAI(
  userId: string,
  privacyConsentVersion: string
): Promise<any> {
  return apiRequest(`/api/users/${userId}/ai/opt-in`, {
    method: 'POST',
    body: JSON.stringify({ privacy_consent_version: privacyConsentVersion }),
  });
}

/**
 * AI opt-out
 */
export async function optOutOfAI(
  userId: string,
  deleteChatHistory: boolean = false
): Promise<any> {
  return apiRequest(`/api/users/${userId}/ai/opt-out`, {
    method: 'POST',
    body: JSON.stringify({ delete_chat_history: deleteChatHistory }),
  });
}

// ========================================
// 7. React Hook Integration (Optional)
// ========================================

/**
 * Custom hook for API calls with loading/error states
 */
import { useState, useCallback } from 'react';

export function useApiCall<T, Args extends any[]>(
  apiFunction: (...args: Args) => Promise<T>
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<T | null>(null);

  const execute = useCallback(
    async (...args: Args) => {
      setLoading(true);
      setError(null);

      try {
        const result = await apiFunction(...args);
        setData(result);
        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction]
  );

  return { execute, loading, error, data };
}

// Usage example:
// const { execute: createTask, loading, error } = useApiCall(createEntity);
// await createTask({ required_field: 'value' });

// ========================================
// Best Practices
// ========================================

// 1. Error Handling:
//    - Always catch and handle errors
//    - Provide user-friendly error messages
//    - Log errors for debugging
//    - Handle network errors separately

// 2. Authentication:
//    - Include JWT token in headers
//    - Redirect to login on 401
//    - Refresh tokens if needed
//    - Handle token expiration

// 3. Type Safety:
//    - Define TypeScript interfaces for all requests/responses
//    - Use generics for reusable functions
//    - Avoid 'any' type
//    - Export types for component usage

// 4. Request Configuration:
//    - Set timeout for requests
//    - Handle loading states
//    - Support request cancellation
//    - Add retry logic for failed requests

// 5. Response Handling:
//    - Validate response structure
//    - Transform data if needed
//    - Cache responses when appropriate
//    - Handle pagination correctly

// 6. Security:
//    - Never expose API keys in frontend
//    - Use HTTPS in production
//    - Validate input before sending
//    - Sanitize user input

// 7. Performance:
//    - Debounce search requests
//    - Use query parameters for filtering
//    - Implement pagination
//    - Cache frequently accessed data

// 8. Testing:
//    - Mock API calls in tests
//    - Test error scenarios
//    - Test authentication flows
//    - Test with different response shapes
