"""
Shared configuration module using Pydantic Settings
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Service identification
    service_name: str = "event-platform"
    environment: str = "development"
    debug: bool = False

    # Kafka/Redpanda settings
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_sasl_mechanism: Optional[str] = None
    kafka_sasl_username: Optional[str] = None
    kafka_sasl_password: Optional[str] = None

    # Topic configuration
    topic_users: str = "events.users"
    topic_orders: str = "events.orders"
    topic_payments: str = "events.payments"
    topic_dlq: str = "events.dlq"

    # Consumer settings
    consumer_group_id: str = "event-processor-group"
    consumer_auto_offset_reset: str = "earliest"
    consumer_enable_auto_commit: bool = False
    consumer_max_poll_records: int = 100

    # Producer settings
    producer_acks: str = "all"
    producer_retries: int = 3
    producer_retry_backoff_ms: int = 100

    # Supabase settings
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_db_url: str = ""
    database_url: str = ""

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # Logging
    log_level: str = "INFO"

    # Storage
    parquet_storage_path: str = "./data/parquet"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
