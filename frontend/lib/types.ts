/**
 * TypeScript type definitions for the Todo application.
 *
 * These types define the shape of data structures used throughout
 * the frontend application, ensuring type safety and autocomplete support.
 */

/**
 * Task entity representing a todo item.
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * User entity representing an authenticated user.
 */
export interface User {
  id: string;
  email: string;
  name: string;
}

/**
 * Input data for creating a new task.
 */
export interface CreateTaskInput {
  title: string;
  description?: string;
}

/**
 * Input data for updating an existing task.
 */
export interface UpdateTaskInput {
  title?: string;
  description?: string;
}

/**
 * Input data for user signup.
 */
export interface SignupInput {
  email: string;
  password: string;
  name: string;
}

/**
 * Input data for user login.
 */
export interface LoginInput {
  email: string;
  password: string;
}

/**
 * Response from authentication endpoints (signup/login).
 */
export interface AuthResponse {
  user: User;
  token: string;
}

/**
 * API error response structure.
 */
export interface ApiError {
  detail: string;
}

// ============================================================================
// Phase III: AI Chatbot Integration Types
// ============================================================================

/**
 * User AI preferences.
 */
export interface UserPreferences {
  user_id: string;
  ai_enabled: boolean;
  preferred_language: 'en' | 'ur';
  auto_detect_language: boolean;
  voice_input_enabled: boolean;
  privacy_consent_version?: string;
  ai_opt_in_date?: string;
}

/**
 * Request for AI opt-in.
 */
export interface AIOptInRequest {
  privacy_consent_version?: string;
  preferred_language?: 'en' | 'ur';
}

/**
 * Request for updating AI preferences.
 */
export interface AIPreferencesUpdate {
  preferred_language?: 'en' | 'ur';
  auto_detect_language?: boolean;
  voice_input_enabled?: boolean;
}

/**
 * Chat conversation.
 */
export interface Conversation {
  id: number;
  user_id: string;
  created_at: string;
  updated_at: string;
}

/**
 * Chat message.
 */
export interface Message {
  id: number;
  user_id: string;
  conversation_id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  language?: 'en' | 'ur';
  related_task_id?: number;
  intent_detected?: string;
  confidence_score?: number;
}

/**
 * Chat message input.
 */
export interface ChatMessageInput {
  message: string;
}
