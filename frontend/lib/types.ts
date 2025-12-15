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
