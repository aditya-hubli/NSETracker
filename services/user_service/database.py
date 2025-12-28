"""Database operations for User Service."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from shared.config import get_settings
from shared.exceptions import DatabaseError, NotFoundError
from shared.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class UserRepository:
    """Repository for user database operations.

    Uses Supabase REST API via httpx for async operations.
    """

    def __init__(self) -> None:
        """Initialize the repository."""
        self.base_url = f"{settings.supabase_url}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_anon_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def create(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new user.

        Args:
            user_data: User data to insert

        Returns:
            Created user data

        Raises:
            DatabaseError: If creation fails
        """
        import httpx

        user_id = str(uuid4())
        now = datetime.now(UTC).isoformat()

        payload = {
            "id": user_id,
            "email": user_data["email"],
            "username": user_data["username"],
            "full_name": user_data.get("full_name"),
            "hashed_password": user_data["hashed_password"],
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/users",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()
                return data[0] if isinstance(data, list) else data
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to create user: {e}")
            raise DatabaseError(
                message="Failed to create user",
                operation="INSERT",
                details={"error": str(e)},
            ) from e

    async def get_by_id(self, user_id: UUID) -> dict[str, Any]:
        """Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User data

        Raises:
            NotFoundError: If user not found
        """
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users",
                    params={"id": f"eq.{user_id}", "select": "*"},
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    raise NotFoundError(resource="User", resource_id=str(user_id))

                return data[0]
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get user: {e}")
            raise DatabaseError(
                message="Failed to get user",
                operation="SELECT",
                details={"error": str(e)},
            ) from e

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        """Get user by email.

        Args:
            email: User email

        Returns:
            User data or None if not found
        """
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users",
                    params={"email": f"eq.{email}", "select": "*"},
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()
                return data[0] if data else None
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get user by email: {e}")
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Get all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user data
        """
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users",
                    params={"select": "*", "offset": skip, "limit": limit},
                    headers={
                        **self.headers,
                        "Range": f"{skip}-{skip + limit - 1}",
                    },
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get users: {e}")
            raise DatabaseError(
                message="Failed to get users",
                operation="SELECT",
                details={"error": str(e)},
            ) from e

    async def update(self, user_id: UUID, update_data: dict[str, Any]) -> dict[str, Any]:
        """Update a user.

        Args:
            user_id: User UUID
            update_data: Data to update

        Returns:
            Updated user data

        Raises:
            NotFoundError: If user not found
        """
        import httpx

        # Add updated timestamp
        update_data["updated_at"] = datetime.now(UTC).isoformat()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/users",
                    params={"id": f"eq.{user_id}"},
                    json=update_data,
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    raise NotFoundError(resource="User", resource_id=str(user_id))

                return data[0]
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to update user: {e}")
            raise DatabaseError(
                message="Failed to update user",
                operation="UPDATE",
                details={"error": str(e)},
            ) from e

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user.

        Args:
            user_id: User UUID

        Returns:
            True if deleted

        Raises:
            NotFoundError: If user not found
        """
        import httpx

        # First check if user exists
        await self.get_by_id(user_id)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/users",
                    params={"id": f"eq.{user_id}"},
                    headers=self.headers,
                )
                response.raise_for_status()
                return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to delete user: {e}")
            raise DatabaseError(
                message="Failed to delete user",
                operation="DELETE",
                details={"error": str(e)},
            ) from e


# Singleton instance
user_repository = UserRepository()
