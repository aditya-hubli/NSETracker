"""
Tests for shared configuration module
"""
import os
import pytest
from unittest.mock import patch


class TestSettings:
    """Test Settings class"""

    def test_default_values(self) -> None:
        """Test default configuration values"""
        from shared.config import Settings

        settings = Settings()

        assert settings.service_name == "event-platform"
        assert settings.environment == "development"
        assert settings.debug is False
        assert settings.kafka_bootstrap_servers == "localhost:9092"
        assert settings.log_level == "INFO"

    def test_env_override(self) -> None:
        """Test environment variable override"""
        from shared.config import Settings

        with patch.dict(os.environ, {
            "SERVICE_NAME": "test-service",
            "ENVIRONMENT": "production",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
        }):
            settings = Settings()

            assert settings.service_name == "test-service"
            assert settings.environment == "production"
            assert settings.debug is True
            assert settings.log_level == "DEBUG"

    def test_kafka_settings(self) -> None:
        """Test Kafka configuration"""
        from shared.config import Settings

        with patch.dict(os.environ, {
            "KAFKA_BOOTSTRAP_SERVERS": "kafka:9092",
            "CONSUMER_GROUP_ID": "test-group",
            "PRODUCER_ACKS": "1",
        }):
            settings = Settings()

            assert settings.kafka_bootstrap_servers == "kafka:9092"
            assert settings.consumer_group_id == "test-group"
            assert settings.producer_acks == "1"

    def test_cors_origins_list(self) -> None:
        """Test CORS origins parsing"""
        from shared.config import Settings

        with patch.dict(os.environ, {
            "CORS_ORIGINS": "http://localhost:3000, http://localhost:8000, https://example.com",
        }):
            settings = Settings()
            origins = settings.cors_origins_list

            assert len(origins) == 3
            assert "http://localhost:3000" in origins
            assert "http://localhost:8000" in origins
            assert "https://example.com" in origins

    def test_topic_configuration(self) -> None:
        """Test topic configuration"""
        from shared.config import Settings

        settings = Settings()

        assert settings.topic_users == "events.users"
        assert settings.topic_orders == "events.orders"
        assert settings.topic_payments == "events.payments"
        assert settings.topic_dlq == "events.dlq"


class TestGetSettings:
    """Test get_settings function"""

    def test_get_settings_cached(self) -> None:
        """Test that settings are cached"""
        from shared.config import get_settings

        # Clear cache
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2
