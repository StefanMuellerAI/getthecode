"""Rate limiter configuration.

Separate module to avoid circular imports between main.py and routers.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings

settings = get_settings()

# PERFORMANCE: Initialize rate limiter with Redis storage for distributed rate limiting
# This ensures rate limits work correctly across multiple backend instances
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    # Use sliding window algorithm for smoother rate limiting
    strategy="moving-window",
)

