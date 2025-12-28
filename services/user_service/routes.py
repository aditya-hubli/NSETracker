"""User Service API Routes."""

import hashlib
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from services.user_service.database import user_repository
from services.user_service.models import User, UserCreate, UserUpdate
from shared.exceptions import DatabaseError, NotFoundError
from shared.logging_config import get_logger
from shared.schemas import EventType, UserEvent

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


def hash_password(password: str) -> str:
    """Hash a password using SHA256.

    Note: In production, use bcrypt or argon2.
    """
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate) -> User:
    """Create a new user.

    Args:
        user_data: User creation data

    Returns:
        Created user

    Raises:
        HTTPException: If email already exists or creation fails
    """
    # Check if email already exists
    existing = await user_repository.get_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    try:
        # Hash password and create user
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hash_password(user_dict.pop("password"))

        created = await user_repository.create(user_dict)

        # Log event (would publish to Redpanda in full implementation)
        event = UserEvent(
            event_type=EventType.USER_CREATED,
            user_id=UUID(created["id"]),
            email=created["email"],
            username=created["username"],
            action="register",
            source="user-service",
        )
        logger.info(f"User created event: {event.event_id}")

        return User(**created)
    except DatabaseError as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        ) from e


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: UUID) -> User:
    """Get a user by ID.

    Args:
        user_id: User UUID

    Returns:
        User data

    Raises:
        HTTPException: If user not found
    """
    try:
        user = await user_repository.get_by_id(user_id)
        return User(**user)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        ) from e
    except DatabaseError as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user",
        ) from e


@router.get("/", response_model=list[User])
async def list_users(skip: int = 0, limit: int = 100) -> list[User]:
    """List all users with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of users
    """
    try:
        users = await user_repository.get_all(skip=skip, limit=limit)
        return [User(**u) for u in users]
    except DatabaseError as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users",
        ) from e


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: UUID, user_data: UserUpdate) -> User:
    """Update a user.

    Args:
        user_id: User UUID
        user_data: Update data

    Returns:
        Updated user

    Raises:
        HTTPException: If user not found or update fails
    """
    try:
        # Filter out None values
        update_dict = {k: v for k, v in user_data.model_dump().items() if v is not None}

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        updated = await user_repository.update(user_id, update_dict)

        # Log event
        event = UserEvent(
            event_type=EventType.USER_UPDATED,
            user_id=user_id,
            email=updated["email"],
            username=updated["username"],
            action="update",
            source="user-service",
        )
        logger.info(f"User updated event: {event.event_id}")

        return User(**updated)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        ) from e
    except DatabaseError as e:
        logger.error(f"Failed to update user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        ) from e


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID) -> None:
    """Delete a user.

    Args:
        user_id: User UUID

    Raises:
        HTTPException: If user not found or deletion fails
    """
    try:
        # Get user first for event
        user = await user_repository.get_by_id(user_id)

        await user_repository.delete(user_id)

        # Log event
        event = UserEvent(
            event_type=EventType.USER_DELETED,
            user_id=user_id,
            email=user["email"],
            username=user["username"],
            action="delete",
            source="user-service",
        )
        logger.info(f"User deleted event: {event.event_id}")

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.message),
        ) from e
    except DatabaseError as e:
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        ) from e
