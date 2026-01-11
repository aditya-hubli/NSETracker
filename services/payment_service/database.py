"""Database operations for Payment Service."""

import secrets
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from shared.config import get_settings
from shared.exceptions import DatabaseError, NotFoundError
from shared.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class PaymentRepository:
    """Repository for payment database operations."""

    def __init__(self) -> None:
        """Initialize the repository."""
        self.base_url = f"{settings.supabase_url}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_anon_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def create(self, payment_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new payment."""
        import httpx

        payment_id = str(uuid4())
        now = datetime.now(UTC).isoformat()

        payload = {
            "id": payment_id,
            "order_id": str(payment_data["order_id"]),
            "user_id": str(payment_data["user_id"]),
            "amount": str(payment_data["amount"]),
            "currency": payment_data.get("currency", "USD"),
            "status": "pending",
            "payment_method": payment_data.get("payment_method", "card"),
            "transaction_id": None,
            "created_at": now,
            "updated_at": now,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payments",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()
                return data[0] if isinstance(data, list) else data
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to create payment: {e}")
            raise DatabaseError(
                message="Failed to create payment",
                operation="INSERT",
                details={"error": str(e)},
            ) from e

    async def get_by_id(self, payment_id: UUID) -> dict[str, Any]:
        """Get payment by ID."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/payments",
                    params={"id": f"eq.{payment_id}", "select": "*"},
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    raise NotFoundError(resource="Payment", resource_id=str(payment_id))

                return data[0]
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get payment: {e}")
            raise DatabaseError(
                message="Failed to get payment",
                operation="SELECT",
                details={"error": str(e)},
            ) from e

    async def get_by_order(self, order_id: UUID) -> list[dict[str, Any]]:
        """Get payments for an order."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/payments",
                    params={"order_id": f"eq.{order_id}", "select": "*"},
                    headers=self.headers,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get order payments: {e}")
            raise DatabaseError(
                message="Failed to get order payments",
                operation="SELECT",
                details={"error": str(e)},
            ) from e

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Get all payments with pagination."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/payments",
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
            logger.error(f"Failed to get payments: {e}")
            raise DatabaseError(
                message="Failed to get payments",
                operation="SELECT",
                details={"error": str(e)},
            ) from e

    async def update_status(
        self,
        payment_id: UUID,
        status: str,
        transaction_id: str | None = None,
    ) -> dict[str, Any]:
        """Update payment status."""
        import httpx

        update_data: dict[str, Any] = {
            "status": status,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        if transaction_id:
            update_data["transaction_id"] = transaction_id

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/payments",
                    params={"id": f"eq.{payment_id}"},
                    json=update_data,
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    raise NotFoundError(resource="Payment", resource_id=str(payment_id))

                return data[0]
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to update payment: {e}")
            raise DatabaseError(
                message="Failed to update payment",
                operation="UPDATE",
                details={"error": str(e)},
            ) from e


payment_repository = PaymentRepository()


def generate_transaction_id() -> str:
    """Generate a mock transaction ID."""
    return f"txn_{secrets.token_hex(12)}"
