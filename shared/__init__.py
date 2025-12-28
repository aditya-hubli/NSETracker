"""Shared module for Real-Time Event-Driven Data Platform.

This module contains shared utilities, schemas, and configurations
used across all microservices in the platform.
"""

from shared.config import Settings, get_settings
from shared.exceptions import (
    BaseAppException,
    ConfigurationError,
    DatabaseError,
    EventProcessingError,
    NotFoundError,
    ValidationError,
)
from shared.schemas import (
    BaseEvent,
    EventType,
    OrderEvent,
    OrderStatus,
    PaymentEvent,
    PaymentStatus,
    UserEvent,
)

__all__ = [
    # Config
    "Settings",
    "get_settings",
    # Exceptions
    "BaseAppException",
    "ConfigurationError",
    "DatabaseError",
    "EventProcessingError",
    "NotFoundError",
    "ValidationError",
    # Schemas
    "BaseEvent",
    "EventType",
    "OrderEvent",
    "OrderStatus",
    "PaymentEvent",
    "PaymentStatus",
    "UserEvent",
]

__version__ = "0.1.0"
