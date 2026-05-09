"""
Application configuration
"""

from typing import List
from pydantic import BaseSettings
from functools import lru_cache


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
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

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


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
