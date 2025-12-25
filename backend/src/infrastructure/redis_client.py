"""
Redis Client Singleton

Provides a singleton Redis connection for:
- WebSocket pub/sub (multi-instance broadcasting)
- Presence tracking (user online/offline status)
- Caching (analytics queries, search results)
"""

import redis.asyncio as redis
from typing import Optional
import logging

from ..config import REDIS_URL, REDIS_ENABLED

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Singleton Redis client for async operations.

    Manages connection pooling and provides methods for:
    - Pub/Sub messaging
    - Key-value storage with TTL
    - Presence tracking
    """

    _instance: Optional['RedisClient'] = None
    _client: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        """
        Establish connection to Redis server.

        Creates connection pool and verifies connectivity.
        """
        if self._client is not None:
            return  # Already connected

        if not REDIS_ENABLED:
            logger.warning("Redis is disabled in configuration")
            return

        try:
            self._client = await redis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50  # Connection pool size
            )

            # Test connection
            await self._client.ping()
            logger.info(f"✅ Connected to Redis at {REDIS_URL}")

        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            logger.warning("Running in single-instance mode (no Redis)")
            self._client = None

    async def disconnect(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            logger.info("Redis connection closed")
            self._client = None

    def get_client(self) -> Optional[redis.Redis]:
        """
        Get Redis client instance.

        Returns:
            Redis client or None if not connected/enabled
        """
        return self._client

    async def publish(self, channel: str, message: str):
        """
        Publish message to Redis channel (for WebSocket broadcasting).

        Args:
            channel: Channel name (e.g., "websocket_broadcast")
            message: Message to publish (JSON string)
        """
        if self._client:
            try:
                await self._client.publish(channel, message)
            except Exception as e:
                logger.error(f"Failed to publish to {channel}: {e}")

    async def subscribe(self, channel: str):
        """
        Subscribe to Redis channel.

        Args:
            channel: Channel name

        Returns:
            PubSub object for receiving messages
        """
        if self._client:
            pubsub = self._client.pubsub()
            await pubsub.subscribe(channel)
            return pubsub
        return None

    async def set_with_ttl(self, key: str, value: str, ttl_seconds: int):
        """
        Set key-value with TTL (for presence tracking).

        Args:
            key: Redis key (e.g., "presence:user123")
            value: Value to store (JSON string)
            ttl_seconds: Time to live in seconds
        """
        if self._client:
            try:
                await self._client.setex(key, ttl_seconds, value)
            except Exception as e:
                logger.error(f"Failed to set {key}: {e}")

    async def get(self, key: str) -> Optional[str]:
        """
        Get value by key.

        Args:
            key: Redis key

        Returns:
            Value or None if not found
        """
        if self._client:
            try:
                return await self._client.get(key)
            except Exception as e:
                logger.error(f"Failed to get {key}: {e}")
        return None

    async def delete(self, key: str):
        """Delete key from Redis"""
        if self._client:
            try:
                await self._client.delete(key)
            except Exception as e:
                logger.error(f"Failed to delete {key}: {e}")

    async def keys_pattern(self, pattern: str) -> list:
        """
        Get all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "presence:*")

        Returns:
            List of matching keys
        """
        if self._client:
            try:
                return await self._client.keys(pattern)
            except Exception as e:
                logger.error(f"Failed to get keys for pattern {pattern}: {e}")
        return []


# Global singleton instance
redis_client = RedisClient()
