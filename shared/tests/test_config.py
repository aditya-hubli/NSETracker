"""Tests for configuration module."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.config import Settings, get_settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings(self) -> None:
        """Test default settings values."""
        settings = Settings(_env_file=None)
        assert settings.environment == "development"
        assert settings.debug is False
        assert settings.redpanda_brokers == "localhost:9092"
        assert settings.service_name == "unknown-service"
        assert settings.service_port == 8000
        assert settings.log_level == "INFO"
        assert settings.log_format == "json"

    def test_environment_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test settings can be overridden by environment variables."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("SERVICE_NAME", "test-service")
        monkeypatch.setenv("SERVICE_PORT", "9000")

        settings = Settings(_env_file=None)
        assert settings.environment == "production"
        assert settings.debug is True
        assert settings.service_name == "test-service"
        assert settings.service_port == 9000

    def test_valid_log_levels(self) -> None:
        """Test valid log levels are accepted."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = Settings(log_level=level, _env_file=None)
            assert settings.log_level == level

    def test_log_level_case_insensitive(self) -> None:
        """Test log level validation is case-insensitive."""
        settings = Settings(log_level="debug", _env_file=None)
        assert settings.log_level == "DEBUG"

        settings = Settings(log_level="Info", _env_file=None)
        assert settings.log_level == "INFO"

    def test_invalid_log_level(self) -> None:
        """Test invalid log level raises error."""
        with pytest.raises(PydanticValidationError):
            Settings(log_level="INVALID", _env_file=None)

    def test_redpanda_broker_list(self) -> None:
        """Test Redpanda broker list parsing."""
        settings = Settings(
            redpanda_brokers="broker1:9092,broker2:9092,broker3:9092",
            _env_file=None,
        )
        assert settings.redpanda_broker_list == [
            "broker1:9092",
            "broker2:9092",
            "broker3:9092",
        ]

    def test_redpanda_broker_list_single(self) -> None:
        """Test single Redpanda broker."""
        settings = Settings(redpanda_brokers="localhost:9092", _env_file=None)
        assert settings.redpanda_broker_list == ["localhost:9092"]

    def test_is_production(self) -> None:
        """Test is_production property."""
        settings = Settings(environment="production", _env_file=None)
        assert settings.is_production is True

        settings = Settings(environment="development", _env_file=None)
        assert settings.is_production is False

    def test_is_test(self) -> None:
        """Test is_test property."""
        settings = Settings(environment="test", _env_file=None)
        assert settings.is_test is True

        settings = Settings(environment="development", _env_file=None)
        assert settings.is_test is False

    def test_valid_environments(self) -> None:
        """Test all valid environment values."""
        for env in ["development", "staging", "production", "test"]:
            settings = Settings(environment=env, _env_file=None)
            assert settings.environment == env

    def test_invalid_environment(self) -> None:
        """Test invalid environment raises error."""
        with pytest.raises(PydanticValidationError):
            Settings(environment="invalid", _env_file=None)

    def test_supabase_settings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Supabase configuration settings."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")
        monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-key")
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/test")

        settings = Settings(_env_file=None)
        assert settings.supabase_url == "https://test.supabase.co"
        assert settings.supabase_anon_key == "test-anon-key"
        assert settings.supabase_service_role_key == "test-service-key"
        assert settings.database_url == "postgresql://localhost/test"


class TestGetSettings:
    """Test cases for get_settings function."""

    def test_get_settings_returns_settings(self) -> None:
        """Test get_settings returns a Settings instance."""
        # Clear cache for test
        get_settings.cache_clear()
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_cached(self) -> None:
        """Test get_settings returns cached instance."""
        get_settings.cache_clear()
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
