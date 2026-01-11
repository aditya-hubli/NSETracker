"""Payment models and schemas."""

from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class PaymentStatus(str, Enum):
    """Payment status enum."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Payment method enum."""

    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    CRYPTO = "crypto"


class PaymentCreate(BaseModel):
    """Schema for creating a payment."""

    order_id: UUID = Field(description="Associated order ID")
    user_id: UUID = Field(description="User making the payment")
    amount: Decimal = Field(ge=0, description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    payment_method: PaymentMethod = Field(
        default=PaymentMethod.CARD, description="Payment method"
    )


class Payment(BaseModel):
    """Payment response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="Payment ID")
    order_id: UUID = Field(description="Order ID")
    user_id: UUID = Field(description="User ID")
    amount: Decimal = Field(ge=0, description="Amount")
    currency: str = Field(default="USD", description="Currency")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Status")
    payment_method: PaymentMethod = Field(description="Payment method")
    transaction_id: str | None = Field(default=None, description="Transaction ID")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Last update timestamp",
    )
