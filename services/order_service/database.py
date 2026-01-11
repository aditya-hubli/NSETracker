"""Database operations for Order Service."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from shared.config import get_settings
from shared.exceptions import DatabaseError, NotFoundError
from shared.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class OrderRepository:
    """Repository for order database operations."""

    def __init__(self) -> None:
        """Initialize the repository."""
        self.base_url = f"{settings.supabase_url}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_anon_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def create(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new order."""
        import httpx

        order_id = str(uuid4())
        now = datetime.now(UTC).isoformat()

        # Calculate total
        total = sum(
            Decimal(str(item["unit_price"])) * item["quantity"]
            for item in order_data["items"]
        )

        payload = {
            "id": order_id,
            "user_id": str(order_data["user_id"]),
            "items": order_data["items"],
            "total_amount": str(total),
            "currency": "USD",
            "status": "pending",
            "shipping_address": order_data["shipping_address"],
            "notes": order_data.get("notes"),
            "created_at": now,
            "updated_at": now,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/orders",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()
                return data[0] if isinstance(data, list) else data
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to create order: {e}")
            raise DatabaseError(
                message="Failed to create order",
                operation="INSERT",
                details={"error": str(e)},
            ) from e

    async def get_by_id(self, order_id: UUID) -> dict[str, Any]:
        """Get order by ID."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/orders",
                    params={"id": f"eq.{order_id}", "select": "*"},
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    raise NotFoundError(resource="Order", resource_id=str(order_id))

                return data[0]
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get order: {e}")
            raise DatabaseError(
                message="Failed to get order",
                operation="SELECT",
                details={"error": str(e)},
            ) from e

    async def get_by_user(self, user_id: UUID) -> list[dict[str, Any]]:
        """Get all orders for a user."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/orders",
                    params={"user_id": f"eq.{user_id}", "select": "*"},
                    headers=self.headers,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get user orders: {e}")
            raise DatabaseError(
                message="Failed to get user orders",
                operation="SELECT",
                details={"error": str(e)},
            ) from e

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Get all orders with pagination."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/orders",
                    params={
                        "select": "*",
                        "order": "created_at.desc",
                        "offset": skip,
                        "limit": limit,
                    },
                    headers=self.headers,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get orders: {e}")
            raise DatabaseError(
                message="Failed to get orders",
                operation="SELECT",
                details={"error": str(e)},
            ) from e

    async def update(
        self, order_id: UUID, update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an order."""
        import httpx

        update_data["updated_at"] = datetime.now(UTC).isoformat()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/orders",
                    params={"id": f"eq.{order_id}"},
                    json=update_data,
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    raise NotFoundError(resource="Order", resource_id=str(order_id))

                return data[0]
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to update order: {e}")
            raise DatabaseError(
                message="Failed to update order",
                operation="UPDATE",
                details={"error": str(e)},
            ) from e


order_repository = OrderRepository()
