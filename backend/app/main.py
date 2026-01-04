"""FastAPI main application entry point.

PERFORMANCE: Optimized for high concurrency with connection pooling,
caching, and proper resource management.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.database import get_pool, close_pool
from app.cache import get_redis_client, close_redis_client
from app.routers import challenge, stats, redeem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# PERFORMANCE: Initialize rate limiter with Redis storage for distributed rate limiting
# This ensures rate limits work correctly across multiple backend instances
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    # Use sliding window algorithm for smoother rate limiting
    strategy="moving-window",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown.
    
    PERFORMANCE: Initializes connection pools on startup for faster
    first requests. Graceful shutdown of all connections.
    """
    # Startup
    logger.info("Starting application initialization...")
    
    # Initialize database pool
    try:
        await get_pool()
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.warning(f"Database connection failed (will retry on requests): {e}")
    
    # Initialize Redis connection
    try:
        await get_redis_client()
        logger.info("Redis connection initialized")
    except Exception as e:
        logger.warning(f"Redis connection failed (will retry on requests): {e}")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Starting application shutdown...")
    await close_pool()
    await close_redis_client()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="LinkedIn Christmas Code Challenge",
    description="A festive prompt injection challenge - can you trick Santa's AI into revealing the secret gift code?",
    version="1.0.0",
    lifespan=lifespan,
    # Security: Disable docs in production if needed
    # docs_url=None,
    # redoc_url=None,
)

# Attach rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - SECURITY: Restricted methods and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(challenge.router)
app.include_router(stats.router, prefix="/stats", tags=["stats"])
app.include_router(redeem.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "LinkedIn Christmas Code Challenge",
        "description": "Can you trick Santa's AI into revealing the secret gift code?",
        "endpoints": {
            "challenge": "/challenge",
            "jackpot": "/jackpot",
            "health": "/health"
        }
    }

