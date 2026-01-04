"""Pydantic models for API requests and responses."""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in the conversation history."""
    role: Literal["user", "assistant"] = Field(
        ..., description="The role of the message sender"
    )
    content: str = Field(
        ..., min_length=1, max_length=2000,
        description="The content of the message"
    )


class ChallengeRequest(BaseModel):
    """Request model for submitting a challenge prompt.
    
    SECURITY: Conversation history is stored server-side in Redis.
    Client only sends conversation_id to prevent history manipulation.
    """
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's current prompt trying to extract the secret code"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Optional conversation ID for multi-turn chats. If not provided, a new conversation starts."
    )


class ChallengeResponse(BaseModel):
    """Response model for a challenge attempt."""
    response: str = Field(..., description="The AI's response to the challenge")
    workflow_id: str = Field(..., description="The Temporal workflow ID for tracking")
    conversation_id: str = Field(..., description="The conversation ID for multi-turn chats")


class JackpotResponse(BaseModel):
    """Response model for jackpot information."""
    amount: int = Field(..., description="Current jackpot amount in euros")
    months_active: int = Field(..., description="Number of months the challenge has been active")
    start_date: str = Field(..., description="The start date of the challenge")
    currency: str = Field(default="EUR", description="Currency of the jackpot")
    code_count: int = Field(default=0, description="Number of available gift codes")
    game_status: str = Field(default="active", description="Current game status")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(default="healthy")
    version: str = Field(default="1.0.0")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WorkflowResult(BaseModel):
    """Internal model for workflow result."""
    final_response: str
    stage1_response: str | None = None
    stage2_response: str | None = None
    stage3_response: str | None = None
    code_detected_at_stage: int | None = None
