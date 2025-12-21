"""Temporal worker for processing challenge workflows.

PERFORMANCE: Configured for high-concurrency workloads with optimal
activity and workflow slot configurations.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the backend directory to the path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from temporalio.client import Client
from temporalio.worker import Worker

from app.config import get_settings
from workflows.challenge_workflow import ChallengeWorkflow
from workflows.activities import (
    generate_response,
    referee_check,
    log_code_leak,
    sanitize_input,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PERFORMANCE: Worker concurrency settings
# These can be overridden via environment variables
MAX_CONCURRENT_ACTIVITIES = int(os.getenv("WORKER_MAX_CONCURRENT_ACTIVITIES", "100"))
MAX_CONCURRENT_WORKFLOWS = int(os.getenv("WORKER_MAX_CONCURRENT_WORKFLOWS", "100"))


async def main():
    """Start the Temporal worker with optimized concurrency settings."""
    settings = get_settings()
    
    logger.info(f"Connecting to Temporal at {settings.temporal_address}...")
    
    # Retry connection with backoff
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            client = await Client.connect(settings.temporal_address)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.info(f"Waiting for Temporal... (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to Temporal after {max_retries} attempts")
                raise
    
    logger.info("Connected to Temporal")
    logger.info(f"Task Queue: {settings.temporal_task_queue}")
    logger.info(f"OpenAI Model: {settings.openai_model}")
    # SECURITY: Do not log any information about the secret code (including length)
    logger.info("Secret code configured: [REDACTED]")
    logger.info("Workflow: Parallel Referees + Final String Match")
    logger.info(f"PERFORMANCE: Max concurrent activities: {MAX_CONCURRENT_ACTIVITIES}")
    logger.info(f"PERFORMANCE: Max concurrent workflows: {MAX_CONCURRENT_WORKFLOWS}")
    
    # PERFORMANCE: Create worker with optimized concurrency settings
    # - max_concurrent_activities: Limit parallel activity executions per worker
    # - max_concurrent_workflow_tasks: Limit parallel workflow task executions
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[ChallengeWorkflow],
        activities=[
            generate_response,
            referee_check,
            log_code_leak,
            sanitize_input,
        ],
        max_concurrent_activities=MAX_CONCURRENT_ACTIVITIES,
        max_concurrent_workflow_tasks=MAX_CONCURRENT_WORKFLOWS,
    )
    
    logger.info("Worker started and listening for tasks...")
    
    # Run the worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
