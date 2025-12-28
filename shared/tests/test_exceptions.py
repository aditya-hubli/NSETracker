"""
Tests for shared exceptions module
"""
import pytest

from shared.exceptions import (
    ErrorCode,
    PlatformException,
    ValidationException,
    KafkaException,
    DatabaseException,
    NotFoundException,
    SerializationException,
)


class TestErrorCode:
    """Test ErrorCode enum"""

    def test_error_codes_exist(self) -> None:
        """Test that all expected error codes exist"""
        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert ErrorCode.KAFKA_CONNECTION_ERROR.value == "KAFKA_CONNECTION_ERROR"
        assert ErrorCode.DATABASE_ERROR.value == "DATABASE_ERROR"
        assert ErrorCode.NOT_FOUND.value == "NOT_FOUND"
        assert ErrorCode.INTERNAL_ERROR.value == "INTERNAL_ERROR"


class TestPlatformException:
    """Test PlatformException class"""

    def test_default_values(self) -> None:
        """Test default exception values"""
        exc = PlatformException("Test error")

        assert exc.message == "Test error"
        assert exc.error_code == ErrorCode.INTERNAL_ERROR
        assert exc.status_code == 500
        assert exc.details == {}

    def test_custom_values(self) -> None:
        """Test custom exception values"""
        exc = PlatformException(
            message="Custom error",
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details={"field": "name"}
        )

        assert exc.message == "Custom error"
        assert exc.error_code == ErrorCode.VALIDATION_ERROR
        assert exc.status_code == 400
        assert exc.details == {"field": "name"}

    def test_to_dict(self) -> None:
        """Test to_dict method"""
        exc = PlatformException(
            message="Test error",
            error_code=ErrorCode.VALIDATION_ERROR,
            details={"key": "value"}
        )

        result = exc.to_dict()

        assert result["error"] == "VALIDATION_ERROR"
        assert result["code"] == "VALIDATION_ERROR"
        assert result["message"] == "Test error"
        assert result["details"] == {"key": "value"}

    def test_exception_inheritance(self) -> None:
        """Test that PlatformException inherits from Exception"""
        exc = PlatformException("Test")
        assert isinstance(exc, Exception)
        assert str(exc) == "Test"


class TestValidationException:
    """Test ValidationException class"""

    def test_defaults(self) -> None:
        """Test validation exception defaults"""
        exc = ValidationException("Invalid input")

        assert exc.message == "Invalid input"
        assert exc.error_code == ErrorCode.VALIDATION_ERROR
        assert exc.status_code == 400

    def test_with_details(self) -> None:
        """Test validation exception with details"""
        exc = ValidationException(
            "Invalid email",
            details={"field": "email", "value": "invalid"}
        )

        assert exc.details["field"] == "email"


class TestKafkaException:
    """Test KafkaException class"""

    def test_defaults(self) -> None:
        """Test Kafka exception defaults"""
        exc = KafkaException("Connection failed")

        assert exc.message == "Connection failed"
        assert exc.error_code == ErrorCode.KAFKA_CONNECTION_ERROR
        assert exc.status_code == 503

    def test_custom_error_code(self) -> None:
        """Test Kafka exception with custom error code"""
        exc = KafkaException(
            "Produce failed",
            error_code=ErrorCode.KAFKA_PRODUCE_ERROR
        )

        assert exc.error_code == ErrorCode.KAFKA_PRODUCE_ERROR


class TestDatabaseException:
    """Test DatabaseException class"""

    def test_defaults(self) -> None:
        """Test database exception defaults"""
        exc = DatabaseException("Query failed")

        assert exc.message == "Query failed"
        assert exc.error_code == ErrorCode.DATABASE_ERROR
        assert exc.status_code == 503


class TestNotFoundException:
    """Test NotFoundException class"""

    def test_defaults(self) -> None:
        """Test not found exception defaults"""
        exc = NotFoundException("Resource not found")

        assert exc.message == "Resource not found"
        assert exc.error_code == ErrorCode.NOT_FOUND
        assert exc.status_code == 404


class TestSerializationException:
    """Test SerializationException class"""

    def test_defaults(self) -> None:
        """Test serialization exception defaults"""
        exc = SerializationException("Failed to serialize")

        assert exc.message == "Failed to serialize"
        assert exc.error_code == ErrorCode.SERIALIZATION_ERROR
        assert exc.status_code == 500
