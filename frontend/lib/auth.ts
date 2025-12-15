/**
 * Authentication utilities for managing user sessions.
 *
 * This module provides helper functions for:
 * - Checking authentication status
 * - Logging out users
 * - Redirecting to login page
 */

import { getAuthToken, getUser, clearAuthToken } from './api';

/**
 * Check if user is currently authenticated.
 *
 * @returns true if user has a valid token, false otherwise
 */
export function isAuthenticated(): boolean {
  const token = getAuthToken();
  const user = getUser();
  return !!token && !!user;
}

/**
 * Get the currently authenticated user.
 *
 * @returns User object or null if not authenticated
 */
export function getCurrentUser() {
  return getUser();
}

/**
 * Log out the current user.
 *
 * - Clears authentication token
 * - Clears user data
 * - Redirects to login page
 */
export function logout(): void {
  clearAuthToken();
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

/**
 * Require authentication for a page.
 *
 * Call this function at the top of protected pages/components.
 * Redirects to login if not authenticated.
 *
 * @returns User object if authenticated
 */
export function requireAuth() {
  if (!isAuthenticated()) {
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    return null;
  }
  return getCurrentUser();
}
