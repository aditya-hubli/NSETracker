"""Tests for exceptions module."""

import pytest

from shared.exceptions import (
    BaseAppException,
    ConfigurationError,
    DatabaseError,
    EventProcessingError,
    NotFoundError,
    ValidationError,
)


class TestBaseAppException:
    """Test cases for BaseAppException."""

    def test_basic_exception(self) -> None:
        """Test creating basic exception."""
        exc = BaseAppException("Something went wrong")
        assert str(exc) == "Something went wrong"
        assert exc.message == "Something went wrong"
        assert exc.error_code == "UNKNOWN_ERROR"
        assert exc.details == {}

    def test_exception_with_code(self) -> None:
        """Test exception with custom error code."""
        exc = BaseAppException("Error", error_code="CUSTOM_ERROR")
        assert exc.error_code == "CUSTOM_ERROR"

    def test_exception_with_details(self) -> None:
        """Test exception with details."""
        exc = BaseAppException(
            "Error",
            details={"field": "email", "reason": "invalid format"},
        )
        assert exc.details == {"field": "email", "reason": "invalid format"}

    def test_to_dict(self) -> None:
        """Test converting exception to dictionary."""
        exc = BaseAppException(
            "Something failed",
            error_code="FAILURE",
            details={"key": "value"},
        )
        result = exc.to_dict()
        assert result == {
            "error": {
                "code": "FAILURE",
                "message": "Something failed",
                "details": {"key": "value"},
            }
        }


class TestValidationError:
    """Test cases for ValidationError."""

    def test_validation_error(self) -> None:
        """Test basic validation error."""
        exc = ValidationError("Invalid email format")
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.message == "Invalid email format"

    def test_validation_error_with_field(self) -> None:
        """Test validation error with field."""
        exc = ValidationError("Invalid format", field="email")
        assert exc.field == "email"
        assert exc.details["field"] == "email"

    def test_validation_error_to_dict(self) -> None:
        """Test validation error dictionary conversion."""
        exc = ValidationError("Too short", field="password")
        result = exc.to_dict()
        assert result["error"]["code"] == "VALIDATION_ERROR"
        assert result["error"]["details"]["field"] == "password"


class TestNotFoundError:
    """Test cases for NotFoundError."""

    def test_not_found_error_basic(self) -> None:
        """Test basic not found error."""
        exc = NotFoundError("User")
        assert exc.error_code == "NOT_FOUND"
        assert exc.message == "User not found"
        assert exc.resource == "User"
        assert exc.resource_id is None

    def test_not_found_error_with_id(self) -> None:
        """Test not found error with resource ID."""
        exc = NotFoundError("User", resource_id="123")
        assert exc.message == "User with ID '123' not found"
        assert exc.resource_id == "123"
        assert exc.details["resource"] == "User"
        assert exc.details["resource_id"] == "123"

    def test_not_found_error_to_dict(self) -> None:
        """Test not found error dictionary conversion."""
        exc = NotFoundError("Order", resource_id="ord-456")
        result = exc.to_dict()
        assert result["error"]["code"] == "NOT_FOUND"
        assert result["error"]["details"]["resource"] == "Order"
        assert result["error"]["details"]["resource_id"] == "ord-456"


class TestDatabaseError:
    """Test cases for DatabaseError."""

    def test_database_error_basic(self) -> None:
        """Test basic database error."""
        exc = DatabaseError("Connection failed")
        assert exc.error_code == "DATABASE_ERROR"
        assert exc.message == "Connection failed"
        assert exc.operation is None

    def test_database_error_with_operation(self) -> None:
        """Test database error with operation."""
        exc = DatabaseError("Insert failed", operation="INSERT")
        assert exc.operation == "INSERT"
        assert exc.details["operation"] == "INSERT"

    def test_database_error_to_dict(self) -> None:
        """Test database error dictionary conversion."""
        exc = DatabaseError("Query timeout", operation="SELECT")
        result = exc.to_dict()
        assert result["error"]["code"] == "DATABASE_ERROR"
        assert result["error"]["details"]["operation"] == "SELECT"


class TestConfigurationError:
    """Test cases for ConfigurationError."""

    def test_configuration_error_basic(self) -> None:
        """Test basic configuration error."""
        exc = ConfigurationError("Missing required configuration")
        assert exc.error_code == "CONFIGURATION_ERROR"
        assert exc.message == "Missing required configuration"
        assert exc.setting is None

    def test_configuration_error_with_setting(self) -> None:
        """Test configuration error with setting name."""
        exc = ConfigurationError("Invalid value", setting="DATABASE_URL")
        assert exc.setting == "DATABASE_URL"
        assert exc.details["setting"] == "DATABASE_URL"

    def test_configuration_error_to_dict(self) -> None:
        """Test configuration error dictionary conversion."""
        exc = ConfigurationError("Not set", setting="API_KEY")
        result = exc.to_dict()
        assert result["error"]["code"] == "CONFIGURATION_ERROR"
        assert result["error"]["details"]["setting"] == "API_KEY"


class TestEventProcessingError:
    """Test cases for EventProcessingError."""

    def test_event_processing_error_basic(self) -> None:
        """Test basic event processing error."""
        exc = EventProcessingError("Failed to process event")
        assert exc.error_code == "EVENT_PROCESSING_ERROR"
        assert exc.message == "Failed to process event"
        assert exc.event_type is None
        assert exc.event_id is None

    def test_event_processing_error_with_event_info(self) -> None:
        """Test event processing error with event info."""
        exc = EventProcessingError(
            "Deserialization failed",
            event_type="user.created",
            event_id="evt-123",
        )
        assert exc.event_type == "user.created"
        assert exc.event_id == "evt-123"
        assert exc.details["event_type"] == "user.created"
        assert exc.details["event_id"] == "evt-123"

    def test_event_processing_error_to_dict(self) -> None:
        """Test event processing error dictionary conversion."""
        exc = EventProcessingError(
            "Processing timeout",
            event_type="order.created",
            event_id="evt-456",
        )
        result = exc.to_dict()
        assert result["error"]["code"] == "EVENT_PROCESSING_ERROR"
        assert result["error"]["details"]["event_type"] == "order.created"
        assert result["error"]["details"]["event_id"] == "evt-456"


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_base(self) -> None:
        """Test all custom exceptions inherit from BaseAppException."""
        exceptions = [
            ValidationError("test"),
            NotFoundError("test"),
            DatabaseError("test"),
            ConfigurationError("test"),
            EventProcessingError("test"),
        ]
        for exc in exceptions:
            assert isinstance(exc, BaseAppException)
            assert isinstance(exc, Exception)

    def test_exceptions_can_be_raised(self) -> None:
        """Test exceptions can be raised and caught."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Invalid input", field="name")
        assert exc_info.value.field == "name"

        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError("User", resource_id="123")
        assert exc_info.value.resource_id == "123"

    def test_exceptions_catchable_as_base(self) -> None:
        """Test specific exceptions can be caught as BaseAppException."""
        with pytest.raises(BaseAppException):
            raise ValidationError("test")

        with pytest.raises(BaseAppException):
            raise NotFoundError("test")
