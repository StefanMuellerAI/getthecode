"""Stats API endpoints for the admin dashboard.

Provides read-only access to conversation data and analytics.
Protected by a secret key in the URL path.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.config import get_settings
from app.database import (
    get_stats_overview,
    get_conversations,
    get_conversation_messages,
    get_conversation_count,
    get_all_gift_codes,
    add_gift_code,
    get_all_claims,
    get_pending_claims,
    approve_claim,
    reject_claim,
    create_redemption,
    link_claim_to_redemption,
    set_game_status,
    get_game_status,
    get_jackpot_value,
)
from app.cache import cache_delete, CACHE_KEY_JACKPOT

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter()


# Response models
class StatsOverviewResponse(BaseModel):
    """Overview statistics."""
    total_conversations: int
    total_messages: int
    conversations_with_leaks: int
    messages_code_detected: int
    referee_stops: int
    recent_conversations_24h: int


class ConversationSummary(BaseModel):
    """Summary of a conversation."""
    id: str
    created_at: Optional[str]
    last_message_at: Optional[str]
    message_count: int
    has_code_leak: bool


class ConversationsListResponse(BaseModel):
    """Paginated list of conversations."""
    conversations: list[ConversationSummary]
    total: int
    limit: int
    offset: int


class MessageDetail(BaseModel):
    """Detailed message with referee data."""
    id: int
    role: str
    content: str
    sanitized_content: Optional[str]
    referee2_decision: Optional[str]
    referee2_reasoning: Optional[str]
    referee3_decision: Optional[str]
    referee3_reasoning: Optional[str]
    code_detected: bool
    detection_method: Optional[str]
    created_at: Optional[str]


class ConversationDetailResponse(BaseModel):
    """Full conversation with all messages."""
    conversation_id: str
    messages: list[MessageDetail]


class GiftCodeItem(BaseModel):
    """Gift code item."""
    id: int
    code: str
    value: int
    added_at: Optional[str]
    burned_at: Optional[str]
    winner_conversation_id: Optional[str]
    is_available: bool


class GiftCodesListResponse(BaseModel):
    """List of gift codes."""
    codes: list[GiftCodeItem]
    total_available_value: int
    available_count: int


class AddGiftCodeRequest(BaseModel):
    """Request to add a new gift code."""
    code: str
    value: int = 100


class AddGiftCodeResponse(BaseModel):
    """Response after adding a gift code."""
    success: bool
    code_id: Optional[int] = None
    message: str


class ClaimItem(BaseModel):
    """Winner claim item."""
    id: int
    conversation_id: str
    claimed_code: str
    email: str
    claim_message: Optional[str]
    ip_address: Optional[str]
    created_at: Optional[str]
    status: str
    reviewed_at: Optional[str]
    reviewed_by: Optional[str]
    review_notes: Optional[str]


class ClaimsListResponse(BaseModel):
    """List of claims."""
    claims: list[ClaimItem]
    pending_count: int


class ClaimReviewRequest(BaseModel):
    """Request to review a claim."""
    review_notes: Optional[str] = None


class ClaimReviewResponse(BaseModel):
    """Response after reviewing a claim."""
    success: bool
    redemption_token: Optional[str] = None
    message: str


class GameStatusAdminResponse(BaseModel):
    """Game status for admin."""
    status: str
    jackpot_value: int
    code_count: int
    last_winner_conversation_id: Optional[str]
    last_win_at: Optional[str]


class ResetGameRequest(BaseModel):
    """Request to reset game status."""
    new_status: str = "active"


def verify_secret_key(secret_key: str) -> None:
    """Verify the secret key matches the configured value."""
    if secret_key != settings.stats_secret_key:
        logger.warning(f"Invalid stats secret key attempted: {secret_key[:8]}...")
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )


@router.get("/{secret_key}/overview", response_model=StatsOverviewResponse)
async def get_overview(secret_key: str):
    """
    Get overview statistics for the admin dashboard.
    
    Returns aggregated metrics about conversations and security events.
    """
    verify_secret_key(secret_key)
    
    try:
        overview = await get_stats_overview()
        return StatsOverviewResponse(**overview)
    except Exception as e:
        logger.error(f"Failed to get stats overview: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve statistics"
        )


@router.get("/{secret_key}/conversations", response_model=ConversationsListResponse)
async def list_conversations(
    secret_key: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    only_leaks: bool = Query(default=False, description="Filter to only show conversations with code leaks")
):
    """
    Get a paginated list of conversations.
    
    Supports filtering to show only conversations where code was detected.
    """
    verify_secret_key(secret_key)
    
    try:
        conversations = await get_conversations(
            limit=limit,
            offset=offset,
            only_with_leaks=only_leaks
        )
        total = await get_conversation_count()
        
        return ConversationsListResponse(
            conversations=[ConversationSummary(**c) for c in conversations],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Failed to get conversations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversations"
        )


@router.get("/{secret_key}/conversation/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation_detail(secret_key: str, conversation_id: str):
    """
    Get full details of a specific conversation.
    
    Includes all messages with their referee decisions and security flags.
    """
    verify_secret_key(secret_key)
    
    # Validate conversation_id format
    if not conversation_id.startswith("conv-") or len(conversation_id) > 50:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID format"
        )
    
    try:
        messages = await get_conversation_messages(conversation_id)
        
        if not messages:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        
        return ConversationDetailResponse(
            conversation_id=conversation_id,
            messages=[MessageDetail(**m) for m in messages]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversation"
        )


# ===========================================
# GIFT CODE MANAGEMENT
# ===========================================

@router.get("/{secret_key}/codes", response_model=GiftCodesListResponse)
async def list_gift_codes(secret_key: str):
    """
    Get all gift codes (available and burned).
    """
    verify_secret_key(secret_key)
    
    try:
        codes = await get_all_gift_codes()
        available = [c for c in codes if c["is_available"]]
        total_available_value = sum(c["value"] for c in available)
        
        return GiftCodesListResponse(
            codes=[GiftCodeItem(**c) for c in codes],
            total_available_value=total_available_value,
            available_count=len(available)
        )
    except Exception as e:
        logger.error(f"Failed to get gift codes: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve gift codes"
        )


@router.post("/{secret_key}/codes", response_model=AddGiftCodeResponse)
async def add_new_gift_code(secret_key: str, request: AddGiftCodeRequest):
    """
    Add a new gift code.
    Automatically resets game status to 'active' if it was 'redeemed'.
    """
    verify_secret_key(secret_key)
    
    try:
        code_id = await add_gift_code(request.code, request.value)
        
        if code_id:
            # Auto-reset game status to active when adding new codes
            current_status = await get_game_status()
            if current_status["status"] == "redeemed":
                await set_game_status("active")
                logger.info("Game status auto-reset to 'active' after adding new gift code")
            
            # Invalidate jackpot cache so frontend gets updated data
            await cache_delete(CACHE_KEY_JACKPOT)
            
            return AddGiftCodeResponse(
                success=True,
                code_id=code_id,
                message=f"Gift code added successfully with value {request.value}€"
            )
        else:
            return AddGiftCodeResponse(
                success=False,
                message="Failed to add gift code"
            )
    except Exception as e:
        logger.error(f"Failed to add gift code: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to add gift code"
        )


# ===========================================
# CLAIMS MANAGEMENT
# ===========================================

@router.get("/{secret_key}/claims", response_model=ClaimsListResponse)
async def list_claims(secret_key: str):
    """
    Get all claims.
    """
    verify_secret_key(secret_key)
    
    try:
        claims = await get_all_claims()
        pending = [c for c in claims if c["status"] == "pending"]
        
        return ClaimsListResponse(
            claims=[ClaimItem(**c) for c in claims],
            pending_count=len(pending)
        )
    except Exception as e:
        logger.error(f"Failed to get claims: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve claims"
        )


@router.post("/{secret_key}/claims/{claim_id}/approve", response_model=ClaimReviewResponse)
async def approve_winner_claim(
    secret_key: str,
    claim_id: int,
    request: ClaimReviewRequest
):
    """
    Approve a winner claim and generate redemption token.
    """
    verify_secret_key(secret_key)
    
    try:
        import secrets
        
        # Approve the claim
        result = await approve_claim(
            claim_id=claim_id,
            reviewed_by="admin",
            review_notes=request.review_notes
        )
        
        if not result:
            return ClaimReviewResponse(
                success=False,
                message="Claim not found or already reviewed"
            )
        
        # Generate redemption token
        token = secrets.token_urlsafe(64)
        redemption_id = await create_redemption(
            token=token,
            conversation_id=result["conversation_id"],
            detection_method="manual_claim",
            claim_id=claim_id
        )
        
        if redemption_id:
            await link_claim_to_redemption(claim_id, redemption_id)
            # Update game status to pending_claim (pauses the game)
            # Status changes to "redeemed" when the winner actually redeems the codes
            await set_game_status("pending_claim", result["conversation_id"])
        
        return ClaimReviewResponse(
            success=True,
            redemption_token=token,
            message=f"Claim approved! Redemption URL: {settings.frontend_url}/redeem/{token}"
        )
    except Exception as e:
        logger.error(f"Failed to approve claim {claim_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to approve claim"
        )


@router.post("/{secret_key}/claims/{claim_id}/reject", response_model=ClaimReviewResponse)
async def reject_winner_claim(
    secret_key: str,
    claim_id: int,
    request: ClaimReviewRequest
):
    """
    Reject a winner claim.
    """
    verify_secret_key(secret_key)
    
    try:
        result = await reject_claim(
            claim_id=claim_id,
            reviewed_by="admin",
            review_notes=request.review_notes
        )
        
        if result:
            # Reset game status back to active
            await set_game_status("active")
            return ClaimReviewResponse(
                success=True,
                message="Claim rejected"
            )
        else:
            return ClaimReviewResponse(
                success=False,
                message="Claim not found or already reviewed"
            )
    except Exception as e:
        logger.error(f"Failed to reject claim {claim_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to reject claim"
        )


# ===========================================
# GAME STATUS MANAGEMENT
# ===========================================

@router.get("/{secret_key}/game-status", response_model=GameStatusAdminResponse)
async def get_admin_game_status(secret_key: str):
    """
    Get current game status for admin.
    """
    verify_secret_key(secret_key)
    
    try:
        status = await get_game_status()
        jackpot = await get_jackpot_value()
        
        return GameStatusAdminResponse(
            status=status["status"],
            jackpot_value=jackpot["total_value"],
            code_count=jackpot["code_count"],
            last_winner_conversation_id=status.get("last_winner_conversation_id"),
            last_win_at=status.get("last_win_at")
        )
    except Exception as e:
        logger.error(f"Failed to get game status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve game status"
        )


@router.post("/{secret_key}/game-status/reset", response_model=ClaimReviewResponse)
async def reset_game_status(secret_key: str, request: ResetGameRequest):
    """
    Reset game status to a new state.
    Use with caution!
    """
    verify_secret_key(secret_key)
    
    if request.new_status not in ["active", "won", "pending_claim", "redeemed"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Must be: active, won, pending_claim, or redeemed"
        )
    
    try:
        await set_game_status(request.new_status)
        # Invalidate jackpot cache so frontend gets updated data
        await cache_delete(CACHE_KEY_JACKPOT)
        return ClaimReviewResponse(
            success=True,
            message=f"Game status reset to: {request.new_status}"
        )
    except Exception as e:
        logger.error(f"Failed to reset game status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to reset game status"
        )

