FROM python:3.11-slim

# SECURITY: Set environment variables
# PERFORMANCE: WEB_CONCURRENCY controls number of gunicorn workers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    WEB_CONCURRENCY=4

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# SECURITY: Create non-root user
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy application code
COPY --chown=appuser:appgroup . .

# SECURITY: Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# PERFORMANCE: Use Gunicorn with Uvicorn workers for production
# - Workers: controlled by WEB_CONCURRENCY env var (default: 4)
# - Worker class: uvicorn.workers.UvicornWorker for async support
# - Timeout: 120s for AI processing requests
# - Keep-alive: 5s to match nginx upstream keepalive
CMD ["gunicorn", "app.main:app", \
     "--bind", "0.0.0.0:8000", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]

