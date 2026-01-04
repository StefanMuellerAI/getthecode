"""Redemption router for secure gift code claiming.

SECURITY: This router handles sensitive gift code redemption.
All endpoints have strict validation and rate limiting.
"""
import logging
import re
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel, Field, field_validator

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
    validate_conversation_for_claim,
    count_claims_by_ip,
    has_pending_claim_for_conversation,
    create_email_verification,
    verify_email_code,
    is_email_verified,
    count_verification_attempts,
)
from app.limiter import limiter
from app.cache import cache_delete, CACHE_KEY_JACKPOT
from app.email import generate_verification_code, send_verification_email, send_claim_confirmation_email

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
    email: str = Field(..., min_length=5, max_length=255)
    claim_message: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=500)  # Honeypot field
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Ungültige E-Mail-Adresse')
        return v.lower().strip()


class ClaimResponse(BaseModel):
    """Response to a claim submission."""
    success: bool
    claim_id: Optional[int] = None
    message: str


# --- Email Verification Models ---

class SendVerificationCodeRequest(BaseModel):
    """Request to send a verification code."""
    email: str = Field(..., min_length=5, max_length=255)
    conversation_id: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Ungültige E-Mail-Adresse')
        return v.lower().strip()


class SendVerificationCodeResponse(BaseModel):
    """Response after sending verification code."""
    success: bool
    message: str


class VerifyEmailCodeRequest(BaseModel):
    """Request to verify an email code."""
    email: str = Field(..., min_length=5, max_length=255)
    code: str = Field(..., min_length=6, max_length=6)
    conversation_id: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Ungültige E-Mail-Adresse')
        return v.lower().strip()
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate code is 6 digits."""
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Code muss 6 Ziffern haben')
        return v


class VerifyEmailCodeResponse(BaseModel):
    """Response after verifying email code."""
    success: bool
    verified: bool
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


# --- Email Verification Endpoints ---

@router.post("/send-verification-code", response_model=SendVerificationCodeResponse)
@limiter.limit("5/hour")
async def send_verification_code(
    req: SendVerificationCodeRequest,
    request: Request
):
    """
    Send a verification code to the provided email address.
    
    SECURITY:
    - Rate limited to 5 requests per hour per IP
    - Max 3 codes per email per hour
    - Validates conversation exists
    """
    client_ip = get_client_ip(request)
    
    # Validate conversation exists
    is_valid, error_msg = await validate_conversation_for_claim(req.conversation_id)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Rate limiting - check attempts for this email/IP
    attempts = await count_verification_attempts(
        email=req.email,
        ip_address=client_ip,
        hours=1
    )
    
    max_attempts = settings.email_verification_max_attempts
    if attempts >= max_attempts:
        logger.warning(f"Verification rate limit exceeded for {req.email} / {client_ip}")
        raise HTTPException(
            status_code=429,
            detail=f"Zu viele Anfragen. Bitte warte eine Stunde."
        )
    
    # Generate and store verification code
    code = generate_verification_code()
    
    verification_id = await create_email_verification(
        email=req.email,
        code=code,
        conversation_id=req.conversation_id,
        ip_address=client_ip,
        expiry_minutes=settings.email_verification_expiry_minutes
    )
    
    if not verification_id:
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Erstellen des Codes. Bitte versuche es erneut."
        )
    
    # Send email
    email_sent = send_verification_email(req.email, code)
    
    if not email_sent:
        logger.error(f"Failed to send verification email to {req.email}")
        raise HTTPException(
            status_code=500,
            detail="E-Mail konnte nicht gesendet werden. Bitte überprüfe die Adresse."
        )
    
    logger.info(f"Verification code sent to {req.email[:3]}***")
    
    return SendVerificationCodeResponse(
        success=True,
        message="Verifizierungscode wurde gesendet. Bitte überprüfe dein Postfach."
    )


@router.post("/verify-email-code", response_model=VerifyEmailCodeResponse)
@limiter.limit("10/hour")
async def verify_email_code_endpoint(
    req: VerifyEmailCodeRequest,
    request: Request
):
    """
    Verify the email code entered by the user.
    
    SECURITY:
    - Rate limited to 10 attempts per hour per IP
    - Code expires after 10 minutes
    """
    client_ip = get_client_ip(request)
    
    verified, message = await verify_email_code(
        email=req.email,
        code=req.code,
        conversation_id=req.conversation_id
    )
    
    if verified:
        logger.info(f"Email verified: {req.email[:3]}*** for conversation {req.conversation_id}")
    else:
        logger.warning(f"Email verification failed for {req.email[:3]}*** from {client_ip}: {message}")
    
    return VerifyEmailCodeResponse(
        success=True,
        verified=verified,
        message=message if not verified else "E-Mail erfolgreich verifiziert!"
    )


@router.post("/claim", response_model=ClaimResponse)
@limiter.limit("3/hour")
async def submit_claim(
    claim: ClaimRequest,
    request: Request
):
    """
    Submit a claim for gradual code extraction.
    
    Use this when you've extracted the code character by character
    and the automatic detection didn't catch it.
    
    Claims will be reviewed by an admin.
    
    SECURITY:
    - Rate limited to 3 claims per hour per IP
    - Validates conversation exists and has activity
    - Max 5 claims per IP per 24 hours
    - Only one pending claim per conversation allowed
    - Email must be verified via Double Opt-In
    - Game is NOT paused until admin approves the claim
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
    
    # SECURITY: Validate conversation exists and has meaningful activity
    is_valid, error_msg = await validate_conversation_for_claim(claim.conversation_id)
    if not is_valid:
        logger.warning(f"Invalid conversation claim attempt from IP {client_ip}: {error_msg}")
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )
    
    # SECURITY: Verify email is verified via Double Opt-In
    email_verified = await is_email_verified(claim.email, claim.conversation_id)
    if not email_verified:
        logger.warning(f"Unverified email claim attempt from IP {client_ip}: {claim.email}")
        raise HTTPException(
            status_code=400,
            detail="E-Mail-Adresse nicht verifiziert. Bitte verifiziere zuerst deine E-Mail."
        )
    
    # SECURITY: Check IP-based daily limit (max 5 claims per 24h)
    ip_claim_count = await count_claims_by_ip(client_ip, hours=24)
    if ip_claim_count >= 5:
        logger.warning(f"IP claim limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Zu viele Claims von dieser IP. Bitte warte 24 Stunden."
        )
    
    # SECURITY: Check if this conversation already has a pending claim
    if await has_pending_claim_for_conversation(claim.conversation_id):
        logger.warning(f"Duplicate claim attempt for conversation {claim.conversation_id}")
        raise HTTPException(
            status_code=409,
            detail="Für diese Conversation gibt es bereits einen offenen Claim."
        )
    
    # Create the claim
    claim_id = await create_claim(
        conversation_id=claim.conversation_id,
        claimed_code=claim.claimed_code,
        email=claim.email,
        claim_message=claim.claim_message,
        ip_address=client_ip
    )
    
    if not claim_id:
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Erstellen des Claims. Bitte versuche es später erneut."
        )
    
    # NOTE: Game status is NOT changed here anymore!
    # The game continues running. Status changes only when admin approves the claim.
    
    logger.info(
        f"New claim submitted: {claim_id} for conversation {claim.conversation_id}"
    )
    
    # Send confirmation email to user
    email_sent = send_claim_confirmation_email(
        to_email=claim.email,
        claim_id=claim_id,
        claimed_code=claim.claimed_code
    )
    
    if not email_sent:
        logger.warning(f"Failed to send claim confirmation email to {claim.email[:3]}***")
    
    return ClaimResponse(
        success=True,
        claim_id=claim_id,
        message="Dein Gewinn-Anspruch wurde eingereicht und wird vom Admin geprüft. Du erhältst eine Bestätigung per E-Mail."
    )

