"""
Rate Limiter for API endpoints.

Implements a simple in-memory sliding window rate limiter
to prevent API abuse and ensure fair usage.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict
import os


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window.

    Tracks request timestamps per user and enforces limits.
    """

    def __init__(
        self,
        max_requests: int = 10,
        window_seconds: int = 60
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store timestamps per user: {user_id: [timestamp1, timestamp2, ...]}
        self.requests: Dict[str, List[datetime]] = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        """
        Check if a request from user is allowed.

        Args:
            user_id: User identifier

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)

        # Get user's request history
        user_requests = self.requests[user_id]

        # Remove old requests outside the window
        user_requests[:] = [ts for ts in user_requests if ts > cutoff]

        # Check if user has exceeded the limit
        if len(user_requests) >= self.max_requests:
            return False

        # Add current request
        user_requests.append(now)
        return True

    def get_remaining(self, user_id: str) -> int:
        """
        Get remaining requests for user in current window.

        Args:
            user_id: User identifier

        Returns:
            Number of remaining requests
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)

        # Get user's request history
        user_requests = self.requests[user_id]

        # Count valid requests in current window
        valid_requests = [ts for ts in user_requests if ts > cutoff]
        return max(0, self.max_requests - len(valid_requests))

    def get_reset_time(self, user_id: str) -> int:
        """
        Get seconds until rate limit resets for user.

        Args:
            user_id: User identifier

        Returns:
            Seconds until oldest request expires
        """
        now = datetime.utcnow()
        user_requests = self.requests[user_id]

        if not user_requests:
            return 0

        oldest_request = min(user_requests)
        reset_time = oldest_request + timedelta(seconds=self.window_seconds)
        seconds_until_reset = (reset_time - now).total_seconds()

        return max(0, int(seconds_until_reset))

    def clear_user(self, user_id: str):
        """
        Clear rate limit data for a user.

        Args:
            user_id: User identifier
        """
        if user_id in self.requests:
            del self.requests[user_id]


# Global rate limiter instances
# Chat endpoint: 10 messages per minute per user
chat_rate_limiter = RateLimiter(
    max_requests=int(os.getenv("CHAT_RATE_LIMIT_PER_USER", "10")),
    window_seconds=int(os.getenv("CHAT_RATE_LIMIT_WINDOW", "60"))
)

# API endpoint: 100 requests per minute per user (general API calls)
api_rate_limiter = RateLimiter(
    max_requests=int(os.getenv("API_RATE_LIMIT_PER_USER", "100")),
    window_seconds=int(os.getenv("API_RATE_LIMIT_WINDOW", "60"))
)
