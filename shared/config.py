"""Configuration management for the platform.

This module uses Pydantic Settings to manage configuration
from environment variables with type validation.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        description="Current environment",
    )
    debug: bool = Field(
        default=False,
        description="Debug mode flag",
    )

    # Supabase Configuration
    supabase_url: str = Field(
        default="",
        description="Supabase project URL",
    )
    supabase_anon_key: str = Field(
        default="",
        description="Supabase anonymous key",
    )
    supabase_service_role_key: str = Field(
        default="",
        description="Supabase service role key",
    )
    database_url: str = Field(
        default="",
        description="PostgreSQL database URL",
    )

    # Redpanda Configuration
    redpanda_brokers: str = Field(
        default="localhost:9092",
        description="Comma-separated list of Redpanda brokers",
    )
    redpanda_security_protocol: str = Field(
        default="PLAINTEXT",
        description="Security protocol for Redpanda",
    )

    # Service Configuration
    service_name: str = Field(
        default="unknown-service",
        description="Name of the current service",
    )
    service_port: int = Field(
        default=8000,
        description="Port for the service",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    log_format: Literal["json", "text"] = Field(
        default="json",
        description="Log output format",
    )

    # In-Memory Cache Configuration
    cache_ttl: int = Field(
        default=300,
        description="Default cache TTL in seconds",
    )
    cache_max_size: int = Field(
        default=1000,
        description="Maximum number of items in cache",
    )

    # Kafka/Redpanda Event Streaming
    kafka_brokers: str = Field(
        default="localhost:9092",
        description="Comma-separated list of Kafka/Redpanda brokers",
    )
    kafka_consumer_group: str = Field(
        default="stock-platform",
        description="Kafka consumer group ID",
    )

    # External API Keys
    news_api_key: str = Field(
        default="",
        description="NewsAPI.org API key",
    )
    reddit_client_id: str = Field(
        default="",
        description="Reddit API client ID",
    )
    reddit_client_secret: str = Field(
        default="",
        description="Reddit API client secret",
    )
    twitter_bearer_token: str = Field(
        default="",
        description="Twitter API bearer token",
    )

    # JWT Configuration
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )
    jwt_expiration_hours: int = Field(
        default=24,
        description="JWT token expiration in hours",
    )

    # Email Configuration
    smtp_host: str = Field(
        default="smtp.gmail.com",
        description="SMTP server host",
    )
    smtp_port: int = Field(
        default=587,
        description="SMTP server port",
    )
    smtp_username: str = Field(
        default="",
        description="SMTP username/email",
    )
    smtp_password: str = Field(
        default="",
        description="SMTP password or app-specific password",
    )
    smtp_from_email: str = Field(
        default="",
        description="From email address for notifications",
    )
    smtp_from_name: str = Field(
        default="Stock Platform Alerts",
        description="From name for email notifications",
    )
    email_enabled: bool = Field(
        default=False,
        description="Enable email notifications",
    )
    
    # Resend API (simpler alternative to SMTP)
    resend_api_key: str = Field(
        default="",
        description="Resend API key for sending emails",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper_v = v.upper()
        if upper_v not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return upper_v

    @property
    def redpanda_broker_list(self) -> list[str]:
        """Return list of Redpanda brokers."""
        return [b.strip() for b in self.redpanda_brokers.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_test(self) -> bool:
        """Check if running in test mode."""
        return self.environment == "test"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application settings singleton
    """
    return Settings()
