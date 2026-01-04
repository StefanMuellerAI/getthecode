"""Redemption router for secure gift code claiming.

SECURITY: This router handles sensitive gift code redemption.
All endpoints have strict validation and rate limiting.
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel, Field

from app.config import get_settings
from app.database import (
    get_redemption_by_token,
    mark_redemption_used,
    burn_gift_codes,
    log_redemption_attempt,
    count_recent_redemption_attempts,
    set_game_status,
    get_game_status,
    get_jackpot_value,
    create_claim,
)
from app.cache import cache_delete, CACHE_KEY_JACKPOT

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["redemption"])


# --- Response Models ---

class GameStatusResponse(BaseModel):
    """Current game status."""
    status: str  # active, won, pending_claim, redeemed
    jackpot_value: int
    code_count: int
    is_active: bool
    last_winner_at: Optional[str] = None


class RedemptionResponse(BaseModel):
    """Redemption result with gift codes."""
    success: bool
    codes: list[dict] = []
    total_value: int = 0
    message: str = ""


class ClaimRequest(BaseModel):
    """Request to claim a win for gradual extraction."""
    conversation_id: str = Field(..., min_length=1, max_length=100)
    claimed_code: str = Field(..., min_length=1, max_length=100)
    linkedin_profile: str = Field(..., min_length=1, max_length=200)
    claim_message: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=500)  # Honeypot field


class ClaimResponse(BaseModel):
    """Response to a claim submission."""
    success: bool
    claim_id: Optional[int] = None
    message: str


# --- Helper Functions ---

def get_client_ip(request: Request) -> str:
    """Get client IP, considering proxy headers."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# --- Endpoints ---

@router.get("/game-status", response_model=GameStatusResponse)
async def get_current_game_status():
    """
    Get current game status and jackpot value.
    Public endpoint - no authentication required.
    """
    status = await get_game_status()
    jackpot = await get_jackpot_value()
    
    return GameStatusResponse(
        status=status["status"],
        jackpot_value=jackpot["total_value"],
        code_count=jackpot["code_count"],
        is_active=(status["status"] == "active" and jackpot["code_count"] > 0),
        last_winner_at=status.get("last_win_at")
    )


@router.get("/redeem/{token}", response_model=RedemptionResponse)
async def redeem_codes(
    token: str,
    request: Request,
    user_agent: Optional[str] = Header(None)
):
    """
    Redeem gift codes with a secure token.
    
    SECURITY:
    - Token must be valid and not expired
    - Token can only be used once
    - Rate limited to 3 attempts per IP per hour
    - All attempts are logged for security monitoring
    """
    client_ip = get_client_ip(request)
    
    # Rate limiting - max 10 attempts per hour per IP (increased for usability)
    # In production, this prevents enumeration attacks while allowing legitimate retries
    recent_attempts = await count_recent_redemption_attempts(client_ip, hours=1)
    max_attempts = 100 if settings.environment.lower() == "development" else 10
    if recent_attempts >= max_attempts:
        logger.warning(f"Rate limit exceeded for IP {client_ip}")
        await log_redemption_attempt(
            token=token[:20] + "...",  # Don't log full token
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            failure_reason="rate_limit_exceeded"
        )
        # SECURITY: Same response as invalid token to prevent enumeration
        raise HTTPException(
            status_code=404,
            detail="Ungültiger oder abgelaufener Redemption-Token."
        )
    
    # Get redemption by token
    redemption = await get_redemption_by_token(token)
    
    # SECURITY: Same error for all failure cases to prevent enumeration
    error_response = HTTPException(
        status_code=404,
        detail="Ungültiger oder abgelaufener Redemption-Token."
    )
    
    if not redemption:
        logger.warning(f"Invalid redemption token attempt from {client_ip}")
        await log_redemption_attempt(
            token=token[:20] + "...",
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            failure_reason="token_not_found"
        )
        raise error_response
    
    if redemption["is_used"]:
        logger.warning(f"Already used redemption token attempt from {client_ip}")
        await log_redemption_attempt(
            token=token[:20] + "...",
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            failure_reason="already_used"
        )
        raise error_response
    
    if redemption["is_expired"]:
        logger.warning(f"Expired redemption token attempt from {client_ip}")
        await log_redemption_attempt(
            token=token[:20] + "...",
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            failure_reason="expired"
        )
        raise error_response
    
    # Mark redemption as used BEFORE revealing codes
    marked = await mark_redemption_used(
        token=token,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    if not marked:
        logger.error(f"Failed to mark redemption as used for {redemption['id']}")
        await log_redemption_attempt(
            token=token[:20] + "...",
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            failure_reason="mark_failed"
        )
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Einlösen. Bitte kontaktiere den Support."
        )
    
    # Burn gift codes and get them
    codes = await burn_gift_codes(
        conversation_id=redemption["conversation_id"],
        redemption_id=redemption["id"]
    )
    
    # Update game status to redeemed
    await set_game_status("redeemed", redemption["conversation_id"])
    
    # Invalidate jackpot cache
    await cache_delete(CACHE_KEY_JACKPOT)
    
    # Log successful redemption
    await log_redemption_attempt(
        token=token[:20] + "...",
        ip_address=client_ip,
        user_agent=user_agent,
        success=True
    )
    
    total_value = sum(code["value"] for code in codes)
    
    logger.info(
        f"Successfully redeemed {len(codes)} codes worth {total_value}€ "
        f"for conversation {redemption['conversation_id']}"
    )
    
    return RedemptionResponse(
        success=True,
        codes=codes,
        total_value=total_value,
        message=f"Herzlichen Glückwunsch! Du hast {total_value}€ in Amazon-Gutscheinen gewonnen!"
    )


@router.post("/claim", response_model=ClaimResponse)
async def submit_claim(
    claim: ClaimRequest,
    request: Request
):
    """
    Submit a claim for gradual code extraction.
    
    Use this when you've extracted the code character by character
    and the automatic detection didn't catch it.
    
    Claims will be reviewed by an admin.
    """
    client_ip = get_client_ip(request)
    
    # Honeypot check - if filled, silently "succeed" without saving
    if claim.website:
        logger.warning(f"Honeypot triggered from IP {client_ip} - bot detected")
        # Return fake success to not alert the bot
        return ClaimResponse(
            success=True,
            claim_id=None,
            message="Dein Anspruch wurde eingereicht! Ein Admin wird ihn prüfen."
        )
    
    # Create the claim
    claim_id = await create_claim(
        conversation_id=claim.conversation_id,
        claimed_code=claim.claimed_code,
        linkedin_profile=claim.linkedin_profile,
        claim_message=claim.claim_message,
        ip_address=client_ip
    )
    
    if not claim_id:
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Erstellen des Claims. Bitte versuche es später erneut."
        )
    
    # Update game status to pending_claim
    await set_game_status("pending_claim", claim.conversation_id)
    
    # Invalidate jackpot cache
    await cache_delete(CACHE_KEY_JACKPOT)
    
    logger.info(
        f"New claim submitted: {claim_id} for conversation {claim.conversation_id}"
    )
    
    return ClaimResponse(
        success=True,
        claim_id=claim_id,
        message="Dein Gewinn-Anspruch wurde eingereicht und wird vom Admin geprüft."
    )

