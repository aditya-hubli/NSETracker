"""
Tests for shared schemas module
"""
from datetime import datetime
from uuid import UUID
import pytest

from shared.schemas import (
    BaseEvent,
    UserEvent,
    UserEventType,
    UserData,
    OrderEvent,
    OrderEventType,
    OrderData,
    OrderItem,
    PaymentEvent,
    PaymentEventType,
    PaymentData,
    HealthResponse,
    EventResponse,
    ErrorResponse,
)


class TestBaseEvent:
    """Test BaseEvent model"""

    def test_default_values(self) -> None:
        """Test default value generation"""
        event = BaseEvent()

        assert isinstance(event.event_id, UUID)
        assert isinstance(event.timestamp, datetime)
        assert event.version == "1.0"
        assert event.correlation_id is None
        assert event.metadata == {}

    def test_custom_values(self) -> None:
        """Test with custom values"""
        event = BaseEvent(
            version="2.0",
            correlation_id="test-123",
            metadata={"key": "value"}
        )

        assert event.version == "2.0"
        assert event.correlation_id == "test-123"
        assert event.metadata == {"key": "value"}


class TestUserEvent:
    """Test UserEvent model"""

    def test_user_created_event(self) -> None:
        """Test user created event"""
        data = UserData(
            user_id="user-123",
            email="test@example.com",
            name="Test User",
            action="signup"
        )
        event = UserEvent(
            event_type=UserEventType.USER_CREATED,
            data=data
        )

        assert event.event_type == UserEventType.USER_CREATED
        assert event.topic == "events.users"
        assert event.data.user_id == "user-123"
        assert event.data.email == "test@example.com"

    def test_user_event_types(self) -> None:
        """Test all user event types"""
        types = [
            UserEventType.USER_CREATED,
            UserEventType.USER_UPDATED,
            UserEventType.USER_DELETED,
            UserEventType.USER_LOGIN,
            UserEventType.USER_LOGOUT,
        ]
        for event_type in types:
            data = UserData(user_id="user-123")
            event = UserEvent(event_type=event_type, data=data)
            assert event.event_type == event_type


class TestOrderEvent:
    """Test OrderEvent model"""

    def test_order_placed_event(self) -> None:
        """Test order placed event"""
        items = [
            OrderItem(
                product_id="prod-1",
                name="Product 1",
                quantity=2,
                unit_price=10.99
            ),
            OrderItem(
                product_id="prod-2",
                name="Product 2",
                quantity=1,
                unit_price=25.50
            ),
        ]
        data = OrderData(
            order_id="order-123",
            user_id="user-456",
            items=items,
            total_amount=47.48,
            currency="USD"
        )
        event = OrderEvent(
            event_type=OrderEventType.ORDER_PLACED,
            data=data
        )

        assert event.event_type == OrderEventType.ORDER_PLACED
        assert event.topic == "events.orders"
        assert len(event.data.items) == 2
        assert event.data.total_amount == 47.48

    def test_order_event_types(self) -> None:
        """Test all order event types"""
        types = [
            OrderEventType.ORDER_PLACED,
            OrderEventType.ORDER_CONFIRMED,
            OrderEventType.ORDER_SHIPPED,
            OrderEventType.ORDER_DELIVERED,
            OrderEventType.ORDER_CANCELLED,
        ]
        for event_type in types:
            data = OrderData(
                order_id="order-123",
                user_id="user-456",
                total_amount=100.0
            )
            event = OrderEvent(event_type=event_type, data=data)
            assert event.event_type == event_type


class TestPaymentEvent:
    """Test PaymentEvent model"""

    def test_payment_completed_event(self) -> None:
        """Test payment completed event"""
        data = PaymentData(
            payment_id="pay-123",
            order_id="order-456",
            user_id="user-789",
            amount=99.99,
            currency="USD",
            payment_method="credit_card",
            status="completed"
        )
        event = PaymentEvent(
            event_type=PaymentEventType.PAYMENT_COMPLETED,
            data=data
        )

        assert event.event_type == PaymentEventType.PAYMENT_COMPLETED
        assert event.topic == "events.payments"
        assert event.data.amount == 99.99
        assert event.data.status == "completed"

    def test_payment_failed_event(self) -> None:
        """Test payment failed event with failure reason"""
        data = PaymentData(
            payment_id="pay-123",
            order_id="order-456",
            user_id="user-789",
            amount=99.99,
            status="failed",
            failure_reason="Insufficient funds"
        )
        event = PaymentEvent(
            event_type=PaymentEventType.PAYMENT_FAILED,
            data=data
        )

        assert event.event_type == PaymentEventType.PAYMENT_FAILED
        assert event.data.failure_reason == "Insufficient funds"


class TestResponseModels:
    """Test API response models"""

    def test_health_response(self) -> None:
        """Test health response"""
        response = HealthResponse(service="test-service")

        assert response.status == "healthy"
        assert response.service == "test-service"
        assert response.version == "1.0.0"
        assert isinstance(response.timestamp, datetime)

    def test_event_response(self) -> None:
        """Test event response"""
        response = EventResponse(
            success=True,
            event_id="event-123"
        )

        assert response.success is True
        assert response.event_id == "event-123"
        assert response.message == "Event published successfully"

    def test_error_response(self) -> None:
        """Test error response"""
        response = ErrorResponse(
            error="ValidationError",
            code="VALIDATION_ERROR",
            message="Invalid input",
            details={"field": "email", "error": "invalid format"}
        )

        assert response.error == "ValidationError"
        assert response.code == "VALIDATION_ERROR"
        assert response.details is not None
        assert response.details["field"] == "email"
