"""Pytest configuration and fixtures for integration tests."""
import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope="session")
def secret_code() -> str:
    """Test secret code for referee validation."""
    return "TEST-SECRET-CODE-2024"


@pytest.fixture(scope="session")
def openai_api_key() -> str:
    """Get OpenAI API key from environment."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    return key

