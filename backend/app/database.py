"""Database connection and utilities.

PERFORMANCE: Optimized connection pooling for high-concurrency workloads.
- min_size: Keep connections warm to avoid cold-start latency
- max_size: Support thousands of concurrent requests
- command_timeout: Prevent long-running queries from blocking
- Configured for production with proper timeouts and health checks
"""
from datetime import datetime, timedelta
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


# ===========================================
# STATS: Conversation and Message Functions
# ===========================================

async def create_conversation(conversation_id: str) -> bool:
    """Create a new conversation record."""
    try:
        async with get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO conversations (id, created_at, last_message_at, message_count, has_code_leak)
                VALUES ($1, $2, $2, 0, FALSE)
                ON CONFLICT (id) DO NOTHING
                """,
                conversation_id, datetime.utcnow()
            )
        return True
    except Exception as e:
        logger.error(f"Failed to create conversation {conversation_id}: {e}")
        return False


async def update_conversation(
    conversation_id: str,
    increment_count: bool = True,
    has_code_leak: bool = False
) -> bool:
    """Update conversation metadata."""
    try:
        async with get_connection() as conn:
            if increment_count:
                await conn.execute(
                    """
                    UPDATE conversations 
                    SET last_message_at = $2, 
                        message_count = message_count + 1,
                        has_code_leak = has_code_leak OR $3
                    WHERE id = $1
                    """,
                    conversation_id, datetime.utcnow(), has_code_leak
                )
            else:
                await conn.execute(
                    """
                    UPDATE conversations 
                    SET last_message_at = $2,
                        has_code_leak = has_code_leak OR $3
                    WHERE id = $1
                    """,
                    conversation_id, datetime.utcnow(), has_code_leak
                )
        return True
    except Exception as e:
        logger.error(f"Failed to update conversation {conversation_id}: {e}")
        return False


async def save_message(
    conversation_id: str,
    role: str,
    content: str,
    sanitized_content: str | None = None,
    referee2_decision: str | None = None,
    referee2_reasoning: str | None = None,
    referee3_decision: str | None = None,
    referee3_reasoning: str | None = None,
    code_detected: bool = False,
    detection_method: str | None = None
) -> bool:
    """Save a message with optional referee data."""
    try:
        async with get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO messages (
                    conversation_id, role, content, sanitized_content,
                    referee2_decision, referee2_reasoning,
                    referee3_decision, referee3_reasoning,
                    code_detected, detection_method, created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                conversation_id, role, content, sanitized_content,
                referee2_decision, referee2_reasoning,
                referee3_decision, referee3_reasoning,
                code_detected, detection_method, datetime.utcnow()
            )
        return True
    except Exception as e:
        logger.error(f"Failed to save message for {conversation_id}: {e}")
        return False


async def get_stats_overview() -> dict:
    """Get overview statistics for the admin dashboard."""
    async with get_connection() as conn:
        # Total conversations
        total_conversations = await conn.fetchval(
            "SELECT COUNT(*) FROM conversations"
        )
        
        # Total messages
        total_messages = await conn.fetchval(
            "SELECT COUNT(*) FROM messages"
        )
        
        # Conversations with code leaks
        conversations_with_leaks = await conn.fetchval(
            "SELECT COUNT(*) FROM conversations WHERE has_code_leak = TRUE"
        )
        
        # Messages where code was detected
        messages_code_detected = await conn.fetchval(
            "SELECT COUNT(*) FROM messages WHERE code_detected = TRUE"
        )
        
        # Referee STOP decisions
        referee_stops = await conn.fetchval(
            """
            SELECT COUNT(*) FROM messages 
            WHERE referee2_decision = 'STOP' OR referee3_decision = 'STOP'
            """
        )
        
        # Recent activity (last 24 hours)
        recent_conversations = await conn.fetchval(
            """
            SELECT COUNT(*) FROM conversations 
            WHERE created_at > NOW() - INTERVAL '24 hours'
            """
        )
        
        return {
            "total_conversations": total_conversations or 0,
            "total_messages": total_messages or 0,
            "conversations_with_leaks": conversations_with_leaks or 0,
            "messages_code_detected": messages_code_detected or 0,
            "referee_stops": referee_stops or 0,
            "recent_conversations_24h": recent_conversations or 0
        }


async def get_conversations(
    limit: int = 50,
    offset: int = 0,
    only_with_leaks: bool = False
) -> list[dict]:
    """Get paginated list of conversations."""
    async with get_connection() as conn:
        query = """
            SELECT id, created_at, last_message_at, message_count, has_code_leak
            FROM conversations
        """
        if only_with_leaks:
            query += " WHERE has_code_leak = TRUE"
        query += " ORDER BY last_message_at DESC LIMIT $1 OFFSET $2"
        
        rows = await conn.fetch(query, limit, offset)
        return [
            {
                "id": row["id"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "last_message_at": row["last_message_at"].isoformat() if row["last_message_at"] else None,
                "message_count": row["message_count"],
                "has_code_leak": row["has_code_leak"]
            }
            for row in rows
        ]


async def get_conversation_messages(conversation_id: str) -> list[dict]:
    """Get all messages for a specific conversation."""
    async with get_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT id, role, content, sanitized_content,
                   referee2_decision, referee2_reasoning,
                   referee3_decision, referee3_reasoning,
                   code_detected, detection_method, created_at
            FROM messages
            WHERE conversation_id = $1
            ORDER BY created_at ASC
            """,
            conversation_id
        )
        return [
            {
                "id": row["id"],
                "role": row["role"],
                "content": row["content"],
                "sanitized_content": row["sanitized_content"],
                "referee2_decision": row["referee2_decision"],
                "referee2_reasoning": row["referee2_reasoning"],
                "referee3_decision": row["referee3_decision"],
                "referee3_reasoning": row["referee3_reasoning"],
                "code_detected": row["code_detected"],
                "detection_method": row["detection_method"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
            for row in rows
        ]


async def get_conversation_count() -> int:
    """Get total number of conversations."""
    async with get_connection() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM conversations") or 0


# ===========================================
# GIFT CODE REDEMPTION SYSTEM
# ===========================================

# --- Game Status ---

async def get_game_status() -> dict:
    """Get current game status."""
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM game_status WHERE id = 1")
        if not row:
            return {"status": "active", "last_winner_conversation_id": None, "last_win_at": None}
        return {
            "status": row["status"],
            "last_winner_conversation_id": row["last_winner_conversation_id"],
            "last_win_at": row["last_win_at"].isoformat() if row["last_win_at"] else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
        }


async def set_game_status(
    status: str,
    winner_conversation_id: str | None = None
) -> bool:
    """Update game status."""
    try:
        async with get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO game_status (id, status, last_winner_conversation_id, last_win_at, updated_at)
                VALUES (1, $1, $2, $3, $3)
                ON CONFLICT (id) DO UPDATE SET 
                    status = $1,
                    last_winner_conversation_id = COALESCE($2, game_status.last_winner_conversation_id),
                    last_win_at = CASE WHEN $2 IS NOT NULL THEN $3 ELSE game_status.last_win_at END,
                    updated_at = $3
                """,
                status,
                winner_conversation_id,
                datetime.utcnow()
            )
        return True
    except Exception as e:
        logger.error(f"Failed to set game status: {e}")
        return False


# --- Gift Codes ---

async def get_available_gift_codes() -> list[dict]:
    """Get all available (not burned) gift codes."""
    async with get_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT id, code, value, added_at 
            FROM gift_codes 
            WHERE burned_at IS NULL
            ORDER BY added_at ASC
            """
        )
        return [
            {
                "id": row["id"],
                "code": row["code"],
                "value": row["value"],
                "added_at": row["added_at"].isoformat() if row["added_at"] else None
            }
            for row in rows
        ]


async def get_all_gift_codes() -> list[dict]:
    """Get all gift codes for admin view."""
    async with get_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT id, code, value, added_at, burned_at, winner_conversation_id
            FROM gift_codes 
            ORDER BY added_at DESC
            """
        )
        return [
            {
                "id": row["id"],
                "code": row["code"],
                "value": row["value"],
                "added_at": row["added_at"].isoformat() if row["added_at"] else None,
                "burned_at": row["burned_at"].isoformat() if row["burned_at"] else None,
                "winner_conversation_id": row["winner_conversation_id"],
                "is_available": row["burned_at"] is None
            }
            for row in rows
        ]


async def get_jackpot_value() -> dict:
    """Get total value of available gift codes."""
    async with get_connection() as conn:
        result = await conn.fetchrow(
            """
            SELECT COALESCE(SUM(value), 0) as total_value, COUNT(*) as code_count
            FROM gift_codes 
            WHERE burned_at IS NULL
            """
        )
        return {
            "total_value": result["total_value"] or 0,
            "code_count": result["code_count"] or 0
        }


async def add_gift_code(code: str, value: int = 100) -> int | None:
    """Add a new gift code. Returns the ID or None on failure."""
    try:
        async with get_connection() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO gift_codes (code, value, added_at)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                code, value, datetime.utcnow()
            )
            return row["id"] if row else None
    except Exception as e:
        logger.error(f"Failed to add gift code: {e}")
        return None


async def burn_gift_codes(
    conversation_id: str,
    redemption_id: int
) -> list[dict]:
    """Mark all available codes as burned and return them."""
    try:
        async with get_connection() as conn:
            rows = await conn.fetch(
                """
                UPDATE gift_codes 
                SET burned_at = $1, winner_conversation_id = $2, winner_redemption_id = $3
                WHERE burned_at IS NULL
                RETURNING id, code, value
                """,
                datetime.utcnow(), conversation_id, redemption_id
            )
            return [
                {"id": row["id"], "code": row["code"], "value": row["value"]}
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Failed to burn gift codes: {e}")
        return []


# --- Redemptions ---

async def create_redemption(
    token: str,
    conversation_id: str,
    detection_method: str,
    expires_hours: int = 24,
    claim_id: int | None = None
) -> int | None:
    """Create a new redemption token. Returns the ID or None."""
    try:
        async with get_connection() as conn:
            # Get current jackpot value
            jackpot = await get_jackpot_value()
            
            # Calculate timestamps separately to avoid PostgreSQL type issues
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(hours=expires_hours)
            
            row = await conn.fetchrow(
                """
                INSERT INTO redemptions (
                    token, conversation_id, detection_method, 
                    created_at, expires_at, codes_value, claim_id
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
                """,
                token, conversation_id, detection_method,
                created_at, expires_at, jackpot["total_value"], claim_id
            )
            return row["id"] if row else None
    except Exception as e:
        logger.error(f"Failed to create redemption: {e}")
        return None


async def get_redemption_by_token(token: str) -> dict | None:
    """Get redemption details by token."""
    async with get_connection() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, token, conversation_id, detection_method, 
                   created_at, expires_at, used_at, codes_value
            FROM redemptions
            WHERE token = $1
            """,
            token
        )
        if not row:
            return None
        return {
            "id": row["id"],
            "token": row["token"],
            "conversation_id": row["conversation_id"],
            "detection_method": row["detection_method"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "expires_at": row["expires_at"].isoformat() if row["expires_at"] else None,
            "used_at": row["used_at"].isoformat() if row["used_at"] else None,
            "codes_value": row["codes_value"],
            "is_expired": row["expires_at"] < datetime.utcnow() if row["expires_at"] else False,
            "is_used": row["used_at"] is not None
        }


async def mark_redemption_used(
    token: str,
    ip_address: str | None = None,
    user_agent: str | None = None
) -> bool:
    """Mark a redemption as used."""
    try:
        async with get_connection() as conn:
            result = await conn.execute(
                """
                UPDATE redemptions 
                SET used_at = $1, ip_address = $2, user_agent = $3
                WHERE token = $4 AND used_at IS NULL
                """,
                datetime.utcnow(), ip_address, user_agent, token
            )
            return "UPDATE 1" in result
    except Exception as e:
        logger.error(f"Failed to mark redemption used: {e}")
        return False


async def log_redemption_attempt(
    token: str,
    ip_address: str | None,
    user_agent: str | None,
    success: bool,
    failure_reason: str | None = None
) -> None:
    """Log a redemption attempt for security monitoring."""
    try:
        async with get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO redemption_attempts 
                (token_attempted, ip_address, user_agent, success, failure_reason, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                token, ip_address, user_agent, success, failure_reason, datetime.utcnow()
            )
    except Exception as e:
        logger.error(f"Failed to log redemption attempt: {e}")


async def count_recent_redemption_attempts(ip_address: str, hours: int = 1) -> int:
    """Count recent redemption attempts from an IP for rate limiting."""
    async with get_connection() as conn:
        return await conn.fetchval(
            """
            SELECT COUNT(*) FROM redemption_attempts
            WHERE ip_address = $1 AND created_at > NOW() - INTERVAL '%s hours'
            """ % hours,
            ip_address
        ) or 0


# --- Winner Claims ---

async def create_claim(
    conversation_id: str,
    claimed_code: str,
    linkedin_profile: str | None = None,
    claim_message: str | None = None,
    ip_address: str | None = None
) -> int | None:
    """Create a new winner claim. Returns the ID or None."""
    try:
        async with get_connection() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO winner_claims 
                (conversation_id, claimed_code, linkedin_profile, claim_message, ip_address, created_at, status)
                VALUES ($1, $2, $3, $4, $5, $6, 'pending')
                RETURNING id
                """,
                conversation_id, claimed_code, linkedin_profile, claim_message, ip_address, datetime.utcnow()
            )
            return row["id"] if row else None
    except Exception as e:
        logger.error(f"Failed to create claim: {e}")
        return None


async def get_pending_claims() -> list[dict]:
    """Get all pending claims for admin review."""
    async with get_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT id, conversation_id, claimed_code, linkedin_profile, claim_message, 
                   ip_address, created_at, status
            FROM winner_claims
            WHERE status = 'pending'
            ORDER BY created_at ASC
            """
        )
        return [
            {
                "id": row["id"],
                "conversation_id": row["conversation_id"],
                "claimed_code": row["claimed_code"],
                "linkedin_profile": row["linkedin_profile"],
                "claim_message": row["claim_message"],
                "ip_address": row["ip_address"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "status": row["status"]
            }
            for row in rows
        ]


async def get_all_claims() -> list[dict]:
    """Get all claims for admin view."""
    async with get_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT id, conversation_id, claimed_code, linkedin_profile, claim_message, 
                   ip_address, created_at, status, reviewed_at, reviewed_by, review_notes
            FROM winner_claims
            ORDER BY created_at DESC
            """
        )
        return [
            {
                "id": row["id"],
                "conversation_id": row["conversation_id"],
                "claimed_code": row["claimed_code"],
                "linkedin_profile": row["linkedin_profile"],
                "claim_message": row["claim_message"],
                "ip_address": row["ip_address"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "status": row["status"],
                "reviewed_at": row["reviewed_at"].isoformat() if row["reviewed_at"] else None,
                "reviewed_by": row["reviewed_by"],
                "review_notes": row["review_notes"]
            }
            for row in rows
        ]


async def approve_claim(
    claim_id: int,
    reviewed_by: str,
    review_notes: str | None = None
) -> dict | None:
    """Approve a claim and return the claim details."""
    try:
        async with get_connection() as conn:
            row = await conn.fetchrow(
                """
                UPDATE winner_claims 
                SET status = 'approved', reviewed_at = $1, reviewed_by = $2, review_notes = $3
                WHERE id = $4 AND status = 'pending'
                RETURNING id, conversation_id
                """,
                datetime.utcnow(), reviewed_by, review_notes, claim_id
            )
            if row:
                return {"id": row["id"], "conversation_id": row["conversation_id"]}
            return None
    except Exception as e:
        logger.error(f"Failed to approve claim: {e}")
        return None


async def reject_claim(
    claim_id: int,
    reviewed_by: str,
    review_notes: str | None = None
) -> bool:
    """Reject a claim."""
    try:
        async with get_connection() as conn:
            result = await conn.execute(
                """
                UPDATE winner_claims 
                SET status = 'rejected', reviewed_at = $1, reviewed_by = $2, review_notes = $3
                WHERE id = $4 AND status = 'pending'
                """,
                datetime.utcnow(), reviewed_by, review_notes, claim_id
            )
            return "UPDATE 1" in result
    except Exception as e:
        logger.error(f"Failed to reject claim: {e}")
        return False


async def link_claim_to_redemption(claim_id: int, redemption_id: int) -> bool:
    """Link a claim to its redemption."""
    try:
        async with get_connection() as conn:
            await conn.execute(
                """
                UPDATE winner_claims SET redemption_id = $1 WHERE id = $2
                """,
                redemption_id, claim_id
            )
            return True
    except Exception as e:
        logger.error(f"Failed to link claim to redemption: {e}")
        return False

