"""
Pydantic schemas for event data models
"""
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ==============================================
# ENUMS
# ==============================================
class UserEventType(str, Enum):
    """User event types"""
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"


class OrderEventType(str, Enum):
    """Order event types"""
    ORDER_PLACED = "order_placed"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"


class PaymentEventType(str, Enum):
    """Payment event types"""
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_PROCESSING = "payment_processing"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_REFUNDED = "payment_refunded"


# ==============================================
# BASE EVENT MODEL
# ==============================================
class BaseEvent(BaseModel):
    """Base event model with common fields"""
    event_id: UUID = Field(default_factory=uuid4, description="Unique event identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    version: str = Field(default="1.0", description="Event schema version")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracing")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    }


# ==============================================
# USER EVENTS
# ==============================================
class UserData(BaseModel):
    """User data payload"""
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    action: Optional[str] = None


class UserEvent(BaseEvent):
    """User event model"""
    event_type: UserEventType
    topic: str = "events.users"
    data: UserData


# ==============================================
# ORDER EVENTS
# ==============================================
class OrderItem(BaseModel):
    """Order item model"""
    product_id: str
    name: str
    quantity: int
    unit_price: float


class OrderData(BaseModel):
    """Order data payload"""
    order_id: str
    user_id: str
    items: list[OrderItem] = []
    total_amount: float
    currency: str = "USD"
    status: Optional[str] = None
    shipping_address: Optional[str] = None


class OrderEvent(BaseEvent):
    """Order event model"""
    event_type: OrderEventType
    topic: str = "events.orders"
    data: OrderData


# ==============================================
# PAYMENT EVENTS
# ==============================================
class PaymentData(BaseModel):
    """Payment data payload"""
    payment_id: str
    order_id: str
    user_id: str
    amount: float
    currency: str = "USD"
    payment_method: Optional[str] = None
    status: str
    failure_reason: Optional[str] = None


class PaymentEvent(BaseEvent):
    """Payment event model"""
    event_type: PaymentEventType
    topic: str = "events.payments"
    data: PaymentData


# ==============================================
# API RESPONSE MODELS
# ==============================================
class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EventResponse(BaseModel):
    """Event submission response"""
    success: bool
    event_id: str
    message: str = "Event published successfully"


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    code: str
    message: str
    details: Optional[dict[str, Any]] = None
