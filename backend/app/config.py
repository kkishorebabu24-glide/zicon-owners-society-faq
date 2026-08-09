"""
Application configuration
"""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_TITLE: str = "Society App API"
    API_VERSION: str = "0.1.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/society_db"
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://localhost:8000",
    ]

    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # External APIs
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_ID: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@society-app.com"

    # Feature Flags
    TELEGRAM_INTEGRATION_ENABLED: bool = True
    AI_DIGEST_ENABLED: bool = True
    DEMAND_SUPPLY_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **data):
        super().__init__(**data)
        # Validate SECRET_KEY in production
        if self.ENVIRONMENT == "production" and not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set via environment variable in production")
        
        # Set default in development if not provided
        if not self.SECRET_KEY:
            if self.ENVIRONMENT == "development":
                self.SECRET_KEY = "dev-secret-key-not-for-production-change-immediately"
            else:
                raise ValueError("SECRET_KEY is required")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
