"""
Custom exception classes and error handling utilities
"""
from typing import Any, Optional
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes for the platform"""

    # Validation errors (400)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_EVENT_FORMAT = "INVALID_EVENT_FORMAT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"

    # Authentication/Authorization errors (401/403)
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # Resource errors (404)
    NOT_FOUND = "NOT_FOUND"
    TOPIC_NOT_FOUND = "TOPIC_NOT_FOUND"

    # Conflict errors (409)
    DUPLICATE_EVENT = "DUPLICATE_EVENT"

    # Server errors (500)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    KAFKA_CONNECTION_ERROR = "KAFKA_CONNECTION_ERROR"
    KAFKA_PRODUCE_ERROR = "KAFKA_PRODUCE_ERROR"
    KAFKA_CONSUME_ERROR = "KAFKA_CONSUME_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    SERIALIZATION_ERROR = "SERIALIZATION_ERROR"

    # Service unavailable (503)
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    KAFKA_UNAVAILABLE = "KAFKA_UNAVAILABLE"
    DATABASE_UNAVAILABLE = "DATABASE_UNAVAILABLE"


class PlatformException(Exception):
    """Base exception for the platform"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.error_code.value,
            "code": self.error_code.value,
            "message": self.message,
            "details": self.details,
        }


class ValidationException(PlatformException):
    """Validation error exception"""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details,
        )


class KafkaException(PlatformException):
    """Kafka-related exception"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.KAFKA_CONNECTION_ERROR,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=503,
            details=details,
        )


class DatabaseException(PlatformException):
    """Database-related exception"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.DATABASE_ERROR,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=503,
            details=details,
        )


class NotFoundException(PlatformException):
    """Resource not found exception"""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND,
            status_code=404,
            details=details,
        )


class SerializationException(PlatformException):
    """Serialization/deserialization exception"""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.SERIALIZATION_ERROR,
            status_code=500,
            details=details,
        )
