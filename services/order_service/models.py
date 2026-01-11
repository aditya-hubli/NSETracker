"""Order models and schemas."""

from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    """Order status enum."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    """Order item schema."""

    product_id: str = Field(description="Product identifier")
    product_name: str = Field(description="Product name")
    quantity: int = Field(ge=1, description="Quantity ordered")
    unit_price: Decimal = Field(ge=0, description="Price per unit")

    @property
    def total_price(self) -> Decimal:
        """Calculate total price for this item."""
        return self.unit_price * self.quantity


class OrderCreate(BaseModel):
    """Schema for creating an order."""

    user_id: UUID = Field(description="User placing the order")
    items: list[OrderItem] = Field(min_length=1, description="Order items")
    shipping_address: str = Field(description="Shipping address")
    notes: str | None = Field(default=None, description="Order notes")


class OrderUpdate(BaseModel):
    """Schema for updating an order."""

    status: OrderStatus | None = Field(default=None, description="Order status")
    shipping_address: str | None = Field(default=None, description="Shipping address")
    notes: str | None = Field(default=None, description="Order notes")


class Order(BaseModel):
    """Order response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="Order ID")
    user_id: UUID = Field(description="User ID")
    items: list[OrderItem] = Field(description="Order items")
    total_amount: Decimal = Field(ge=0, description="Total order amount")
    currency: str = Field(default="USD", description="Currency")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Status")
    shipping_address: str = Field(description="Shipping address")
    notes: str | None = Field(default=None, description="Notes")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Last update timestamp",
    )
