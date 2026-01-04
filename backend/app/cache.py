"""Redis cache utilities for high-performance caching.

PERFORMANCE: Provides a centralized caching layer to reduce database load
and support distributed rate limiting across multiple backend instances.
"""
import json
import logging
from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Global Redis client (singleton)
_redis_client: Redis | None = None


async def get_redis_client() -> Redis:
    """Get or create a singleton Redis client.
    
    PERFORMANCE: Reuses the same connection pool across all requests.
    """
    global _redis_client
    if _redis_client is None:
        logger.info(f"Creating Redis connection to {settings.redis_url}")
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            # Connection pool settings for high concurrency
            max_connections=50,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        # Test connection
        try:
            await _redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed (will retry on requests): {e}")
            _redis_client = None
            raise
    return _redis_client


async def close_redis_client():
    """Close the Redis client gracefully."""
    global _redis_client
    if _redis_client is not None:
        logger.info("Closing Redis connection...")
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


async def cache_get(key: str) -> Optional[str]:
    """Get a value from cache.
    
    Returns None if key doesn't exist or Redis is unavailable.
    """
    try:
        client = await get_redis_client()
        return await client.get(key)
    except Exception as e:
        logger.warning(f"Cache get failed for key {key}: {e}")
        return None


async def cache_set(key: str, value: str, ttl: Optional[int] = None) -> bool:
    """Set a value in cache with optional TTL.
    
    Returns True if successful, False otherwise.
    """
    try:
        client = await get_redis_client()
        if ttl is None:
            ttl = settings.redis_cache_ttl
        await client.setex(key, ttl, value)
        return True
    except Exception as e:
        logger.warning(f"Cache set failed for key {key}: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """Delete a key from cache.
    
    Returns True if key was deleted, False otherwise.
    """
    try:
        client = await get_redis_client()
        await client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache delete failed for key {key}: {e}")
        return False


async def cache_get_json(key: str) -> Optional[Any]:
    """Get a JSON value from cache.
    
    Returns None if key doesn't exist or parsing fails.
    """
    value = await cache_get(key)
    if value is not None:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse cached JSON for key {key}")
    return None


async def cache_set_json(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set a JSON value in cache with optional TTL."""
    try:
        json_str = json.dumps(value)
        return await cache_set(key, json_str, ttl)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize value for key {key}: {e}")
        return False


# Cache key constants
CACHE_KEY_JACKPOT = "jackpot:current"
CACHE_KEY_START_DATE = "config:start_date"

# SECURITY: Conversation session settings
CONVERSATION_TTL = 3600  # 1 hour session timeout
CONVERSATION_MAX_MESSAGES = 50  # Max messages per conversation
CONVERSATION_PREFIX = "conversation:"


async def get_conversation(conversation_id: str) -> list[dict]:
    """Get conversation history from Redis.
    
    Returns empty list if conversation doesn't exist or Redis is unavailable.
    """
    key = f"{CONVERSATION_PREFIX}{conversation_id}"
    data = await cache_get_json(key)
    if data is None:
        return []
    return data.get("messages", [])


async def save_conversation(conversation_id: str, messages: list[dict]) -> bool:
    """Save conversation history to Redis.
    
    SECURITY: Limits conversation to max messages to prevent abuse.
    """
    # Enforce message limit
    if len(messages) > CONVERSATION_MAX_MESSAGES:
        messages = messages[-CONVERSATION_MAX_MESSAGES:]
    
    key = f"{CONVERSATION_PREFIX}{conversation_id}"
    return await cache_set_json(key, {"messages": messages}, CONVERSATION_TTL)


async def add_message_to_conversation(
    conversation_id: str, 
    role: str, 
    content: str
) -> bool:
    """Add a single message to conversation history.
    
    Returns True if successful, False otherwise.
    """
    messages = await get_conversation(conversation_id)
    messages.append({"role": role, "content": content})
    return await save_conversation(conversation_id, messages)


async def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation from Redis."""
    key = f"{CONVERSATION_PREFIX}{conversation_id}"
    return await cache_delete(key)

