"""Database connection and utilities.

PERFORMANCE: Optimized connection pooling for high-concurrency workloads.
- min_size: Keep connections warm to avoid cold-start latency
- max_size: Support thousands of concurrent requests
- command_timeout: Prevent long-running queries from blocking
- Configured for production with proper timeouts and health checks
"""
from datetime import datetime
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

import asyncpg
from asyncpg import Pool

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Global connection pool
_pool: Pool | None = None

# Connection pool settings for high performance
POOL_MIN_SIZE = 10  # Keep connections warm
POOL_MAX_SIZE = 100  # Support high concurrency (adjust based on PostgreSQL max_connections)
POOL_COMMAND_TIMEOUT = 30.0  # Timeout for individual commands (seconds)
POOL_MAX_INACTIVE_CONNECTION_LIFETIME = 300.0  # Close idle connections after 5 minutes


async def get_pool() -> Pool:
    """Get or create the database connection pool.
    
    PERFORMANCE: Optimized pool settings for handling thousands of concurrent requests.
    - Maintains warm connections to reduce latency
    - Proper timeouts to prevent resource exhaustion
    - Health checks to detect stale connections
    """
    global _pool
    if _pool is None:
        logger.info(f"Creating database pool (min={POOL_MIN_SIZE}, max={POOL_MAX_SIZE})")
        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=POOL_MIN_SIZE,
            max_size=POOL_MAX_SIZE,
            command_timeout=POOL_COMMAND_TIMEOUT,
            max_inactive_connection_lifetime=POOL_MAX_INACTIVE_CONNECTION_LIFETIME,
        )
        logger.info("Database connection pool initialized")
    return _pool


async def close_pool():
    """Close the database connection pool gracefully."""
    global _pool
    if _pool is not None:
        logger.info("Closing database connection pool...")
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


@asynccontextmanager
async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get a database connection from the pool."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection


async def get_config_value(key: str) -> str | None:
    """Get a configuration value from the database."""
    async with get_connection() as conn:
        row = await conn.fetchrow(
            "SELECT value FROM config WHERE key = $1",
            key
        )
        return row["value"] if row else None


async def set_config_value(key: str, value: str):
    """Set a configuration value in the database."""
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO config (key, value, updated_at) 
            VALUES ($1, $2, $3)
            ON CONFLICT (key) DO UPDATE SET value = $2, updated_at = $3
            """,
            key, value, datetime.utcnow()
        )


async def log_challenge_attempt(
    user_prompt: str,
    ai_response: str,
    code_leaked: bool = False
):
    """Log a challenge attempt to the database."""
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO challenge_attempts (user_prompt, ai_response, code_leaked)
            VALUES ($1, $2, $3)
            """,
            user_prompt, ai_response, code_leaked
        )


async def get_secret_code() -> str:
    """Get the secret code from database or fall back to config."""
    code = await get_config_value("secret_code")
    return code if code else settings.secret_code


async def get_start_date() -> str:
    """Get the start date from database or fall back to config."""
    date = await get_config_value("start_date")
    return date if date else settings.start_date

