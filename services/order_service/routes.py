"""Order Service API Routes."""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from services.order_service.database import order_repository
from services.order_service.models import Order, OrderCreate, OrderUpdate
from shared.exceptions import DatabaseError, NotFoundError
from shared.logging_config import get_logger
from shared.schemas import EventType, OrderEvent

logger = get_logger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate) -> Order:
    """Create a new order."""
    try:
        # Convert items to dict format
        items_dict = [item.model_dump(mode="json") for item in order_data.items]
        order_dict = order_data.model_dump()
        order_dict["items"] = items_dict

        created = await order_repository.create(order_dict)

        # Calculate total for event
        total = sum(
            Decimal(str(item["unit_price"])) * item["quantity"]
            for item in items_dict
        )

        # Log event
        event = OrderEvent(
            event_type=EventType.ORDER_CREATED,
            order_id=UUID(created["id"]),
            user_id=order_data.user_id,
            items=items_dict,
            total_amount=total,
            source="order-service",
        )
        logger.info(f"Order created event: {event.event_id}")

        return Order(**created)
    except DatabaseError as e:
        logger.error(f"Failed to create order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order",
        ) from e


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: UUID) -> Order:
    """Get an order by ID."""
    try:
        order = await order_repository.get_by_id(order_id)
        return Order(**order)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        ) from e
    except DatabaseError as e:
        logger.error(f"Failed to get order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order",
        ) from e


@router.get("/", response_model=list[Order])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    user_id: UUID | None = None,
) -> list[Order]:
    """List orders with optional user filter."""
    try:
        if user_id:
            orders = await order_repository.get_by_user(user_id)
        else:
            orders = await order_repository.get_all(skip=skip, limit=limit)
        return [Order(**o) for o in orders]
    except DatabaseError as e:
        logger.error(f"Failed to list orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list orders",
        ) from e


@router.put("/{order_id}", response_model=Order)
async def update_order(order_id: UUID, order_data: OrderUpdate) -> Order:
    """Update an order."""
    try:
        update_dict = {k: v for k, v in order_data.model_dump().items() if v is not None}

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        # Convert enum to string if present
        if "status" in update_dict:
            update_dict["status"] = update_dict["status"].value

        updated = await order_repository.update(order_id, update_dict)

        # Log event
        event = OrderEvent(
            event_type=EventType.ORDER_UPDATED,
            order_id=order_id,
            user_id=UUID(updated["user_id"]),
            total_amount=Decimal(str(updated["total_amount"])),
            source="order-service",
        )
        logger.info(f"Order updated event: {event.event_id}")

        return Order(**updated)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        ) from e
    except DatabaseError as e:
        logger.error(f"Failed to update order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order",
        ) from e


@router.post("/{order_id}/cancel", response_model=Order)
async def cancel_order(order_id: UUID) -> Order:
    """Cancel an order."""
    try:
        # Get current order
        order = await order_repository.get_by_id(order_id)

        if order["status"] in ["shipped", "delivered"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel shipped or delivered orders",
            )

        updated = await order_repository.update(order_id, {"status": "cancelled"})

        # Log event
        event = OrderEvent(
            event_type=EventType.ORDER_CANCELLED,
            order_id=order_id,
            user_id=UUID(updated["user_id"]),
            total_amount=Decimal(str(updated["total_amount"])),
            source="order-service",
        )
        logger.info(f"Order cancelled event: {event.event_id}")

        return Order(**updated)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        ) from e
    except DatabaseError as e:
        logger.error(f"Failed to cancel order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel order",
        ) from e
