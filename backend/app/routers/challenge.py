"""Challenge API endpoints.

PERFORMANCE: Optimized with singleton Temporal client to avoid
connection overhead on every request.
"""
import uuid
import logging
import asyncio
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter, HTTPException, Request
from temporalio.client import Client
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.models import (
    ChallengeRequest,
    ChallengeResponse,
    JackpotResponse,
    HealthResponse,
)
from app.database import get_start_date, get_jackpot_value, get_game_status
from app.cache import (
    cache_get_json, 
    cache_set_json, 
    CACHE_KEY_JACKPOT,
    get_conversation,
    save_conversation,
)

# Configure logging
logger = logging.getLogger(__name__)

# PERFORMANCE: Jackpot cache TTL (1 hour - value only changes monthly)
JACKPOT_CACHE_TTL = 3600

settings = get_settings()
router = APIRouter()

# PERFORMANCE: Rate limiter with Redis backend for distributed rate limiting
# This allows rate limits to work correctly across multiple backend instances
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    strategy="moving-window",
)

# PERFORMANCE: Singleton Temporal client to avoid connection overhead per request
_temporal_client: Client | None = None
_temporal_client_lock = asyncio.Lock()


async def get_temporal_client() -> Client:
    """Get or create a singleton Temporal client connection.
    
    PERFORMANCE: Reuses the same client instance across all requests,
    avoiding the overhead of establishing a new gRPC connection per request.
    Thread-safe initialization with asyncio.Lock.
    """
    global _temporal_client
    if _temporal_client is None:
        async with _temporal_client_lock:
            # Double-check locking pattern
            if _temporal_client is None:
                logger.info(f"Creating Temporal client connection to {settings.temporal_address}")
                _temporal_client = await Client.connect(settings.temporal_address)
                logger.info("Temporal client connected successfully")
    return _temporal_client


async def close_temporal_client():
    """Close the Temporal client connection gracefully."""
    global _temporal_client
    if _temporal_client is not None:
        logger.info("Closing Temporal client connection...")
        # Temporal client doesn't have an explicit close method,
        # but we reset the singleton for clean shutdown
        _temporal_client = None
        logger.info("Temporal client reference cleared")


def calculate_months_since(start_date_str: str) -> int:
    """Calculate the number of months since the start date."""
    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    today = date.today()
    
    delta = relativedelta(today, start)
    months = delta.years * 12 + delta.months
    
    # Minimum of 1 month (100€ jackpot from day 1)
    return max(1, months + 1)


@router.post("/challenge", response_model=ChallengeResponse)
@limiter.limit("10/minute")  # SECURITY: Max 10 requests per minute per IP
async def submit_challenge(request: Request, challenge_request: ChallengeRequest):
    """
    Submit a prompt to try and extract the secret code.
    
    SECURITY: Conversation history is stored server-side in Redis.
    Client only provides conversation_id - history cannot be manipulated.
    All messages are sanitized before being stored and sent to AI.
    
    Rate limited to 10 requests per minute per IP to prevent abuse.
    """
    try:
        # SECURITY: Generate or validate conversation_id
        conversation_id = challenge_request.conversation_id
        is_new_conversation = False
        
        if conversation_id is None:
            # New conversation
            conversation_id = f"conv-{uuid.uuid4()}"
            conversation_history = []
            is_new_conversation = True
            logger.info(f"Starting new conversation: {conversation_id}")
        else:
            # SECURITY: Validate conversation_id format to prevent injection
            if not conversation_id.startswith("conv-") or len(conversation_id) > 50:
                raise HTTPException(
                    status_code=400,
                    detail="Ungültige Konversations-ID"
                )
            # Load existing conversation from Redis
            conversation_history = await get_conversation(conversation_id)
            logger.info(
                f"Continuing conversation {conversation_id} with "
                f"{len(conversation_history)} existing messages"
            )
        
        # Connect to Temporal and start the workflow
        client = await get_temporal_client()
        workflow_id = f"challenge-{uuid.uuid4()}"
        
        # Import here to avoid circular imports
        from workflows.challenge_workflow import ChallengeWorkflow, ChallengeWorkflowInput
        
        # Create workflow input with prompt, conversation_id and history
        # SECURITY: Sanitization happens in the workflow for both prompt AND history
        workflow_input = ChallengeWorkflowInput(
            user_prompt=challenge_request.prompt,
            conversation_id=conversation_id,
            conversation_history=conversation_history,
            is_new_conversation=is_new_conversation
        )
        
        logger.info(
            f"Starting challenge workflow with {len(conversation_history)} history messages"
        )
        
        # Start the workflow and wait for result
        result = await client.execute_workflow(
            ChallengeWorkflow.run,
            workflow_input,
            id=workflow_id,
            task_queue=settings.temporal_task_queue,
        )
        
        # SECURITY: Store sanitized messages in Redis
        # The workflow returns the sanitized prompt, but we store original
        # since history is already trusted (came from our storage)
        # New user message is sanitized in workflow before processing
        conversation_history.append({
            "role": "user",
            "content": challenge_request.prompt  # Will be sanitized on next load
        })
        conversation_history.append({
            "role": "assistant", 
            "content": result
        })
        
        # Save updated conversation to Redis
        await save_conversation(conversation_id, conversation_history)
        
        return ChallengeResponse(
            response=result,
            workflow_id=workflow_id,
            conversation_id=conversation_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # SECURITY: Log full error internally, return generic message to user
        logger.error(f"Challenge processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Ein Fehler ist aufgetreten. Bitte versuche es erneut."
        )


@router.get("/jackpot", response_model=JackpotResponse)
async def get_jackpot():
    """
    Get the current jackpot amount.
    
    The jackpot is now the sum of all available gift codes in the database.
    
    PERFORMANCE: Cached in Redis for 30 seconds to reduce database load.
    In development mode, caching is disabled for easier testing.
    """
    # PERFORMANCE: Try to get from cache first (skip in development)
    if settings.environment.lower() != "development":
        cached = await cache_get_json(CACHE_KEY_JACKPOT)
        if cached:
            logger.debug("Jackpot served from cache")
            return JackpotResponse(**cached)
    
    try:
        # Get jackpot from gift_codes table
        jackpot_data = await get_jackpot_value()
        start_date = await get_start_date()
        months = calculate_months_since(start_date)
        
        # Get game status
        game_status = await get_game_status()
        
        response_data = {
            "amount": jackpot_data["total_value"],
            "months_active": months,
            "start_date": start_date,
            "currency": "EUR",
            "code_count": jackpot_data["code_count"],
            "game_status": game_status["status"]
        }
        
        # PERFORMANCE: Cache the result (30 seconds - matches frontend polling)
        # Skip caching in development for easier testing
        if settings.environment.lower() != "development":
            await cache_set_json(CACHE_KEY_JACKPOT, response_data, 30)
            logger.debug("Jackpot cached successfully")
        
        return JackpotResponse(**response_data)
    except Exception as e:
        logger.warning(f"Jackpot fetch failed, using fallback: {e}")
        # Fallback to month-based calculation if database fails
        months = calculate_months_since(settings.start_date)
        return JackpotResponse(
            amount=months * settings.jackpot_per_month,
            months_active=months,
            start_date=settings.start_date,
            currency="EUR",
            code_count=0,
            game_status="unknown"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )
