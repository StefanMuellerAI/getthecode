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
from app.database import get_start_date
from app.cache import cache_get_json, cache_set_json, CACHE_KEY_JACKPOT

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
    
    The AI will respond, but three layers of AI verification
    will try to prevent the code from being revealed.
    
    Rate limited to 10 requests per minute per IP to prevent abuse.
    """
    try:
        # Connect to Temporal and start the workflow
        client = await get_temporal_client()
        
        workflow_id = f"challenge-{uuid.uuid4()}"
        
        # Import here to avoid circular imports
        from workflows.challenge_workflow import ChallengeWorkflow
        
        # Start the workflow and wait for result
        # Logging happens inside the workflow when code leak is detected
        result = await client.execute_workflow(
            ChallengeWorkflow.run,
            challenge_request.prompt,
            id=workflow_id,
            task_queue=settings.temporal_task_queue,
        )
        
        return ChallengeResponse(
            response=result,
            workflow_id=workflow_id
        )
        
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
    
    The jackpot increases by 100€ for each month the system
    has successfully protected the code.
    
    PERFORMANCE: Cached in Redis for 1 hour to reduce database load.
    The value only changes monthly, so caching is highly effective.
    """
    # PERFORMANCE: Try to get from cache first
    cached = await cache_get_json(CACHE_KEY_JACKPOT)
    if cached:
        logger.debug("Jackpot served from cache")
        return JackpotResponse(**cached)
    
    try:
        start_date = await get_start_date()
        months = calculate_months_since(start_date)
        amount = months * settings.jackpot_per_month
        
        response_data = {
            "amount": amount,
            "months_active": months,
            "start_date": start_date,
            "currency": "EUR"
        }
        
        # PERFORMANCE: Cache the result
        await cache_set_json(CACHE_KEY_JACKPOT, response_data, JACKPOT_CACHE_TTL)
        logger.debug("Jackpot cached successfully")
        
        return JackpotResponse(**response_data)
    except Exception as e:
        logger.warning(f"Jackpot fetch failed, using fallback: {e}")
        # Fallback to config if database fails
        months = calculate_months_since(settings.start_date)
        return JackpotResponse(
            amount=months * settings.jackpot_per_month,
            months_active=months,
            start_date=settings.start_date,
            currency="EUR"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )

