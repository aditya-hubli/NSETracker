"""Custom exceptions for the platform.

This module defines a hierarchy of custom exceptions
for consistent error handling across services.
"""

from typing import Any


class BaseAppException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            }
        }


class ValidationError(BaseAppException):
    """Exception for validation errors."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            details: Additional details
        """
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=error_details,
        )
        self.field = field


class NotFoundError(BaseAppException):
    """Exception for resource not found errors."""

    def __init__(
        self,
        resource: str,
        resource_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize not found error.

        Args:
            resource: Type of resource not found
            resource_id: ID of the resource
            details: Additional details
        """
        error_details = details or {}
        error_details["resource"] = resource
        if resource_id:
            error_details["resource_id"] = resource_id

        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found"

        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details=error_details,
        )
        self.resource = resource
        self.resource_id = resource_id


class DatabaseError(BaseAppException):
    """Exception for database errors."""

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize database error.

        Args:
            message: Error message
            operation: Database operation that failed
            details: Additional details
        """
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=error_details,
        )
        self.operation = operation


class ConfigurationError(BaseAppException):
    """Exception for configuration errors."""

    def __init__(
        self,
        message: str,
        setting: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            setting: Configuration setting that caused the error
            details: Additional details
        """
        error_details = details or {}
        if setting:
            error_details["setting"] = setting
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=error_details,
        )
        self.setting = setting


class EventProcessingError(BaseAppException):
    """Exception for event processing errors."""

    def __init__(
        self,
        message: str,
        event_type: str | None = None,
        event_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize event processing error.

        Args:
            message: Error message
            event_type: Type of event being processed
            event_id: ID of the event
            details: Additional details
        """
        error_details = details or {}
        if event_type:
            error_details["event_type"] = event_type
        if event_id:
            error_details["event_id"] = event_id
        super().__init__(
            message=message,
            error_code="EVENT_PROCESSING_ERROR",
            details=error_details,
        )
        self.event_type = event_type
        self.event_id = event_id
