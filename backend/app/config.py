"""Application configuration and settings."""
import os
from functools import lru_cache
from typing import Optional, Union, List
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    SECURITY: In production mode (ENVIRONMENT=production), all sensitive values
    MUST be provided via environment variables with strict validation.
    In development mode, default values are allowed for easier local testing.
    """
    
    # Environment mode: "development" or "production"
    environment: str = "development"
    
    # Database
    database_url: str = "postgresql://devuser:devpassword123@localhost:5432/getthecode"
    
    # Temporal
    temporal_host: str = "localhost"
    temporal_port: int = 7233
    temporal_namespace: str = "default"
    temporal_task_queue: str = "challenge-task-queue"
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    
    # Secret Code
    secret_code: str = "DEV-TEST-CODE-1234"
    
    # Challenge Settings
    start_date: str = "2025-01-01"
    jackpot_per_month: int = 100
    
    # PERFORMANCE: Redis for caching and distributed rate limiting
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600  # Cache TTL in seconds (1 hour default)
    
    # CORS - accepts comma-separated string or list
    cors_origins: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000"
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    @model_validator(mode='after')
    def validate_production_settings(self) -> 'Settings':
        """
        SECURITY: In production mode, enforce strict validation of all secrets.
        This prevents accidental deployment with insecure default values.
        """
        if self.environment.lower() == "production":
            # Validate database URL
            if not self.database_url:
                raise ValueError("DATABASE_URL must be provided in production")
            if "devpassword" in self.database_url or "getthecode123" in self.database_url:
                raise ValueError("Default database password detected in production! Use a secure password.")
            
            # Validate secret code
            if not self.secret_code:
                raise ValueError("SECRET_CODE must be provided in production")
            if "DEV" in self.secret_code.upper() or "TEST" in self.secret_code.upper() or "FAKE" in self.secret_code.upper():
                raise ValueError("Development/placeholder secret code detected in production!")
            
            # Validate OpenAI API key
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY must be provided in production")
            if not self.openai_api_key.startswith("sk-"):
                raise ValueError("Invalid OpenAI API key format in production")
        
        return self
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"
    
    @property
    def temporal_address(self) -> str:
        """Get the Temporal server address."""
        return f"{self.temporal_host}:{self.temporal_port}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

