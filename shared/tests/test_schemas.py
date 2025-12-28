"""Tests for schemas module."""

import json
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from shared.schemas import (
    BaseEvent,
    EventType,
    OrderEvent,
    OrderStatus,
    PaymentEvent,
    PaymentStatus,
    UserEvent,
)


class TestEventType:
    """Test cases for EventType enum."""

    def test_user_event_types(self) -> None:
        """Test user event types exist."""
        assert EventType.USER_CREATED == "user.created"
        assert EventType.USER_UPDATED == "user.updated"
        assert EventType.USER_DELETED == "user.deleted"

    def test_order_event_types(self) -> None:
        """Test order event types exist."""
        assert EventType.ORDER_CREATED == "order.created"
        assert EventType.ORDER_UPDATED == "order.updated"
        assert EventType.ORDER_CANCELLED == "order.cancelled"
        assert EventType.ORDER_COMPLETED == "order.completed"

    def test_payment_event_types(self) -> None:
        """Test payment event types exist."""
        assert EventType.PAYMENT_INITIATED == "payment.initiated"
        assert EventType.PAYMENT_COMPLETED == "payment.completed"
        assert EventType.PAYMENT_FAILED == "payment.failed"
        assert EventType.PAYMENT_REFUNDED == "payment.refunded"


class TestOrderStatus:
    """Test cases for OrderStatus enum."""

    def test_order_statuses(self) -> None:
        """Test all order statuses exist."""
        assert OrderStatus.PENDING == "pending"
        assert OrderStatus.CONFIRMED == "confirmed"
        assert OrderStatus.PROCESSING == "processing"
        assert OrderStatus.SHIPPED == "shipped"
        assert OrderStatus.DELIVERED == "delivered"
        assert OrderStatus.CANCELLED == "cancelled"


class TestPaymentStatus:
    """Test cases for PaymentStatus enum."""

    def test_payment_statuses(self) -> None:
        """Test all payment statuses exist."""
        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.PROCESSING == "processing"
        assert PaymentStatus.COMPLETED == "completed"
        assert PaymentStatus.FAILED == "failed"
        assert PaymentStatus.REFUNDED == "refunded"


class TestBaseEvent:
    """Test cases for BaseEvent model."""

    def test_base_event_creation(self) -> None:
        """Test creating a base event."""
        event = BaseEvent(event_type=EventType.USER_CREATED)
        assert isinstance(event.event_id, UUID)
        assert event.event_type == EventType.USER_CREATED
        assert isinstance(event.timestamp, datetime)
        assert event.version == "1.0"
        assert event.source == "unknown"
        assert event.metadata == {}

    def test_base_event_with_custom_values(self) -> None:
        """Test creating a base event with custom values."""
        event_id = uuid4()
        timestamp = datetime.now(UTC)
        event = BaseEvent(
            event_id=event_id,
            event_type=EventType.ORDER_CREATED,
            timestamp=timestamp,
            version="2.0",
            source="test-service",
            metadata={"key": "value"},
        )
        assert event.event_id == event_id
        assert event.timestamp == timestamp
        assert event.version == "2.0"
        assert event.source == "test-service"
        assert event.metadata == {"key": "value"}

    def test_base_event_to_json(self) -> None:
        """Test serializing event to JSON."""
        event = BaseEvent(
            event_type=EventType.USER_CREATED,
            source="test-service",
        )
        json_str = event.to_json()
        data = json.loads(json_str)
        assert data["event_type"] == "user.created"
        assert data["source"] == "test-service"
        assert "event_id" in data
        assert "timestamp" in data


class TestUserEvent:
    """Test cases for UserEvent model."""

    def test_user_event_creation(self) -> None:
        """Test creating a user event."""
        user_id = uuid4()
        event = UserEvent(
            event_type=EventType.USER_CREATED,
            user_id=user_id,
            email="test@example.com",
            username="testuser",
            action="register",
        )
        assert event.user_id == user_id
        assert event.email == "test@example.com"
        assert event.username == "testuser"
        assert event.action == "register"

    def test_user_event_serialization(self) -> None:
        """Test user event JSON serialization."""
        event = UserEvent(
            event_type=EventType.USER_CREATED,
            user_id=uuid4(),
            email="test@example.com",
            username="testuser",
            action="register",
            source="user-service",
        )
        json_str = event.to_json()
        data = json.loads(json_str)
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["action"] == "register"


class TestOrderEvent:
    """Test cases for OrderEvent model."""

    def test_order_event_creation(self) -> None:
        """Test creating an order event."""
        order_id = uuid4()
        user_id = uuid4()
        event = OrderEvent(
            event_type=EventType.ORDER_CREATED,
            order_id=order_id,
            user_id=user_id,
            total_amount=Decimal("99.99"),
        )
        assert event.order_id == order_id
        assert event.user_id == user_id
        assert event.total_amount == Decimal("99.99")
        assert event.currency == "USD"
        assert event.status == OrderStatus.PENDING
        assert event.items == []

    def test_order_event_with_items(self) -> None:
        """Test order event with items."""
        event = OrderEvent(
            event_type=EventType.ORDER_CREATED,
            order_id=uuid4(),
            user_id=uuid4(),
            total_amount=Decimal("199.98"),
            items=[
                {"product_id": "prod-1", "quantity": 2, "price": "99.99"},
            ],
        )
        assert len(event.items) == 1
        assert event.items[0]["product_id"] == "prod-1"

    def test_order_event_status(self) -> None:
        """Test order event with different statuses."""
        event = OrderEvent(
            event_type=EventType.ORDER_UPDATED,
            order_id=uuid4(),
            user_id=uuid4(),
            total_amount=Decimal("50.00"),
            status=OrderStatus.SHIPPED,
        )
        assert event.status == OrderStatus.SHIPPED

    def test_order_event_negative_amount(self) -> None:
        """Test order event rejects negative amount."""
        with pytest.raises(ValueError):
            OrderEvent(
                event_type=EventType.ORDER_CREATED,
                order_id=uuid4(),
                user_id=uuid4(),
                total_amount=Decimal("-10.00"),
            )


class TestPaymentEvent:
    """Test cases for PaymentEvent model."""

    def test_payment_event_creation(self) -> None:
        """Test creating a payment event."""
        payment_id = uuid4()
        order_id = uuid4()
        user_id = uuid4()
        event = PaymentEvent(
            event_type=EventType.PAYMENT_INITIATED,
            payment_id=payment_id,
            order_id=order_id,
            user_id=user_id,
            amount=Decimal("99.99"),
        )
        assert event.payment_id == payment_id
        assert event.order_id == order_id
        assert event.user_id == user_id
        assert event.amount == Decimal("99.99")
        assert event.currency == "USD"
        assert event.status == PaymentStatus.PENDING
        assert event.payment_method == "card"
        assert event.transaction_id is None

    def test_payment_event_completed(self) -> None:
        """Test completed payment event."""
        event = PaymentEvent(
            event_type=EventType.PAYMENT_COMPLETED,
            payment_id=uuid4(),
            order_id=uuid4(),
            user_id=uuid4(),
            amount=Decimal("99.99"),
            status=PaymentStatus.COMPLETED,
            transaction_id="txn_12345",
        )
        assert event.status == PaymentStatus.COMPLETED
        assert event.transaction_id == "txn_12345"

    def test_payment_event_negative_amount(self) -> None:
        """Test payment event rejects negative amount."""
        with pytest.raises(ValueError):
            PaymentEvent(
                event_type=EventType.PAYMENT_INITIATED,
                payment_id=uuid4(),
                order_id=uuid4(),
                user_id=uuid4(),
                amount=Decimal("-10.00"),
            )

    def test_payment_event_serialization(self) -> None:
        """Test payment event JSON serialization."""
        event = PaymentEvent(
            event_type=EventType.PAYMENT_COMPLETED,
            payment_id=uuid4(),
            order_id=uuid4(),
            user_id=uuid4(),
            amount=Decimal("150.00"),
            status=PaymentStatus.COMPLETED,
            payment_method="paypal",
            transaction_id="pp_67890",
        )
        json_str = event.to_json()
        data = json.loads(json_str)
        assert data["amount"] == "150.00"
        assert data["payment_method"] == "paypal"
        assert data["transaction_id"] == "pp_67890"
