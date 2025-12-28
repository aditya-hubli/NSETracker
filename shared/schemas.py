"""Pydantic schemas for events and data models.

This module defines the core event schemas used across
all services for type-safe event processing.
"""

from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class EventType(str, Enum):
    """Types of events in the system."""

    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"

    # Order events
    ORDER_CREATED = "order.created"
    ORDER_UPDATED = "order.updated"
    ORDER_CANCELLED = "order.cancelled"
    ORDER_COMPLETED = "order.completed"

    # Payment events
    PAYMENT_INITIATED = "payment.initiated"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"


class OrderStatus(str, Enum):
    """Status of an order."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    """Status of a payment."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class BaseEvent(BaseModel):
    """Base class for all events."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    event_id: UUID = Field(
        default_factory=uuid4,
        description="Unique event identifier",
    )
    event_type: EventType = Field(
        description="Type of the event",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp in UTC",
    )
    version: str = Field(
        default="1.0",
        description="Event schema version",
    )
    source: str = Field(
        default="unknown",
        description="Service that generated the event",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event metadata",
    )

    def to_json(self) -> str:
        """Serialize event to JSON string."""
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> "BaseEvent":
        """Deserialize event from JSON string."""
        return cls.model_validate_json(data)


class UserEvent(BaseEvent):
    """Event for user-related actions."""

    user_id: UUID = Field(
        description="User identifier",
    )
    email: str = Field(
        description="User email address",
    )
    username: str = Field(
        description="Username",
    )
    action: str = Field(
        description="Action performed",
    )


class OrderEvent(BaseEvent):
    """Event for order-related actions."""

    order_id: UUID = Field(
        description="Order identifier",
    )
    user_id: UUID = Field(
        description="User who placed the order",
    )
    items: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Order items",
    )
    total_amount: Decimal = Field(
        description="Total order amount",
        ge=0,
    )
    currency: str = Field(
        default="USD",
        description="Currency code",
    )
    status: OrderStatus = Field(
        default=OrderStatus.PENDING,
        description="Current order status",
    )


class PaymentEvent(BaseEvent):
    """Event for payment-related actions."""

    payment_id: UUID = Field(
        description="Payment identifier",
    )
    order_id: UUID = Field(
        description="Associated order identifier",
    )
    user_id: UUID = Field(
        description="User making the payment",
    )
    amount: Decimal = Field(
        description="Payment amount",
        ge=0,
    )
    currency: str = Field(
        default="USD",
        description="Currency code",
    )
    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING,
        description="Current payment status",
    )
    payment_method: str = Field(
        default="card",
        description="Payment method used",
    )
    transaction_id: str | None = Field(
        default=None,
        description="External transaction ID",
    )
