"""Redis configuration and cache management for the AI Agent Multi-Model Platform."""

import os
import json
import logging
from typing import Any, Optional
import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_db = int(os.getenv('REDIS_DB', 0))
        self.redis_password = os.getenv('REDIS_PASSWORD')
        self._client = None

    @property
    def client(self) -> redis.Redis:
        """Get or create Redis client with lazy initialization."""
        if self._client is None:
            try:
                self._client = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=self.redis_db,
                    password=self.redis_password,
                    decode_responses=True
                )
                self._client.ping()  # Test connection
                logger.info(f"Connected to Redis at {self.redis_host}:{self.redis_port}")
            except RedisError as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        return self._client

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except RedisError as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration time in seconds."""
        try:
            return self.client.setex(
                key,
                expire,
                json.dumps(value)
            )
        except RedisError as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.client.delete(key))
        except RedisError as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False

    def flush(self) -> bool:
        """Clear all keys in the current database."""
        try:
            return self.client.flushdb()
        except RedisError as e:
            logger.error(f"Error flushing Redis database: {e}")
            return False

# Singleton instance
cache = RedisCache() 