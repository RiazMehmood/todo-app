/**
 * TypeScript type definitions for the Todo application.
 *
 * These types define the shape of data structures used throughout
 * the frontend application, ensuring type safety and autocomplete support.
 */

/**
 * Task priority levels (Phase V).
 */
export type Priority = 'high' | 'medium' | 'low';

/**
 * Recurrence pattern types (Phase V).
 */
export type RecurrencePattern = 'daily' | 'weekly' | 'monthly';

/**
 * Days of the week for recurring tasks (Phase V).
 */
export type DayOfWeek = 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';

/**
 * Task entity representing a todo item.
 *
 * Phase V Enhancement: Added advanced features (recurring tasks, due dates, priorities, tags).
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string | null;
  completed: boolean;

  // Phase V - Intermediate Level: Priorities & Tags
  priority: Priority;
  tags?: string[] | null;

  // Phase V - Advanced Level: Due Dates & Reminders
  due_date?: string | null;
  remind_before_minutes?: number | null;
  reminder_sent: boolean;

  // Phase V - Advanced Level: Recurring Tasks
  is_recurring: boolean;
  recurrence_pattern?: RecurrencePattern | null;
  recurrence_interval?: number | null;
  recurrence_days?: DayOfWeek[] | null;
  recurrence_end_date?: string | null;
  parent_task_id?: number | null;

  // Phase III: AI Metadata
  created_via_ai: boolean;
  ai_suggested_priority?: number | null;
  original_nl_input?: string | null;

  // Timestamps
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
 *
 * Phase V Enhancement: Added advanced features (recurring tasks, due dates, priorities, tags).
 */
export interface CreateTaskInput {
  title: string;
  description?: string;

  // Phase V - Intermediate Level: Priorities & Tags
  priority?: Priority;
  tags?: string[];

  // Phase V - Advanced Level: Due Dates & Reminders
  due_date?: string;
  remind_before_minutes?: number;

  // Phase V - Advanced Level: Recurring Tasks
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
  recurrence_interval?: number;
  recurrence_days?: DayOfWeek[];
  recurrence_end_date?: string;
}

/**
 * Input data for updating an existing task.
 *
 * Phase V Enhancement: Added advanced features (priorities, tags, due dates, reminders).
 */
export interface UpdateTaskInput {
  title?: string;
  description?: string;
  completed?: boolean;

  // Phase V - Intermediate Level: Priorities & Tags
  priority?: Priority;
  tags?: string[];

  // Phase V - Advanced Level: Due Dates & Reminders
  due_date?: string;
  remind_before_minutes?: number;
}

/**
 * Query parameters for filtering and searching tasks (Phase V).
 */
export interface TaskFilterParams {
  status?: 'all' | 'pending' | 'completed';
  priority?: Priority;
  tags?: string; // Comma-separated: "work,urgent"
  search?: string; // Search in title/description
  due_date_before?: string; // ISO datetime
  due_date_after?: string; // ISO datetime
  is_recurring?: boolean;
  sort_by?: 'created_at' | 'due_date' | 'priority' | 'title' | 'updated_at';
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

/**
 * Response from toggle task completion (Phase V).
 *
 * For recurring tasks, includes information about the next created instance.
 */
export interface ToggleTaskResponse {
  task: Task;
  next_task?: Task;
  message?: string;
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
