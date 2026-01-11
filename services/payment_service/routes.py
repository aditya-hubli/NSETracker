"""Payment Service API Routes."""

import asyncio
import random
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from services.payment_service.database import (
    generate_transaction_id,
    payment_repository,
)
from services.payment_service.models import Payment, PaymentCreate, PaymentStatus
from shared.exceptions import DatabaseError, NotFoundError
from shared.logging_config import get_logger
from shared.schemas import EventType, PaymentEvent

logger = get_logger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def create_payment(payment_data: PaymentCreate) -> Payment:
    """Create and process a new payment."""
    try:
        payment_dict = payment_data.model_dump()
        payment_dict["payment_method"] = payment_data.payment_method.value

        created = await payment_repository.create(payment_dict)

        # Log event
        event = PaymentEvent(
            event_type=EventType.PAYMENT_INITIATED,
            payment_id=UUID(created["id"]),
            order_id=payment_data.order_id,
            user_id=payment_data.user_id,
            amount=payment_data.amount,
            source="payment-service",
        )
        logger.info(f"Payment initiated event: {event.event_id}")

        return Payment(**created)
    except DatabaseError as e:
        logger.error(f"Failed to create payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment",
        ) from e


@router.post("/{payment_id}/process", response_model=Payment)
async def process_payment(payment_id: UUID) -> Payment:
    """Process a pending payment (simulated)."""
    try:
        # Get payment
        payment = await payment_repository.get_by_id(payment_id)

        if payment["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment is not pending (current: {payment['status']})",
            )

        # Update to processing
        await payment_repository.update_status(payment_id, "processing")

        # Simulate payment processing delay
        await asyncio.sleep(random.uniform(0.5, 1.5))

        # Simulate success/failure (90% success rate)
        success = random.random() < 0.9

        if success:
            transaction_id = generate_transaction_id()
            updated = await payment_repository.update_status(
                payment_id, "completed", transaction_id
            )

            event = PaymentEvent(
                event_type=EventType.PAYMENT_COMPLETED,
                payment_id=payment_id,
                order_id=UUID(payment["order_id"]),
                user_id=UUID(payment["user_id"]),
                amount=Decimal(str(payment["amount"])),
                transaction_id=transaction_id,
                source="payment-service",
            )
            logger.info(f"Payment completed event: {event.event_id}")
        else:
            updated = await payment_repository.update_status(payment_id, "failed")

            event = PaymentEvent(
                event_type=EventType.PAYMENT_FAILED,
                payment_id=payment_id,
                order_id=UUID(payment["order_id"]),
                user_id=UUID(payment["user_id"]),
                amount=Decimal(str(payment["amount"])),
                source="payment-service",
            )
            logger.info(f"Payment failed event: {event.event_id}")

        return Payment(**updated)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        ) from e
    except DatabaseError as e:
        logger.error(f"Failed to process payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment",
        ) from e


@router.get("/{payment_id}", response_model=Payment)
async def get_payment(payment_id: UUID) -> Payment:
    """Get a payment by ID."""
    try:
        payment = await payment_repository.get_by_id(payment_id)
        return Payment(**payment)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        ) from e
    except DatabaseError as e:
        logger.error(f"Failed to get payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment",
        ) from e


@router.get("/", response_model=list[Payment])
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    order_id: UUID | None = None,
) -> list[Payment]:
    """List payments with optional order filter."""
    try:
        if order_id:
            payments = await payment_repository.get_by_order(order_id)
        else:
            payments = await payment_repository.get_all(skip=skip, limit=limit)
        return [Payment(**p) for p in payments]
    except DatabaseError as e:
        logger.error(f"Failed to list payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list payments",
        ) from e


@router.post("/{payment_id}/refund", response_model=Payment)
async def refund_payment(payment_id: UUID) -> Payment:
    """Refund a completed payment."""
    try:
        payment = await payment_repository.get_by_id(payment_id)

        if payment["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only completed payments can be refunded",
            )

        updated = await payment_repository.update_status(payment_id, "refunded")

        event = PaymentEvent(
            event_type=EventType.PAYMENT_REFUNDED,
            payment_id=payment_id,
            order_id=UUID(payment["order_id"]),
            user_id=UUID(payment["user_id"]),
            amount=Decimal(str(payment["amount"])),
            source="payment-service",
        )
        logger.info(f"Payment refunded event: {event.event_id}")

        return Payment(**updated)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        ) from e
    except DatabaseError as e:
        logger.error(f"Failed to refund payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refund payment",
        ) from e
