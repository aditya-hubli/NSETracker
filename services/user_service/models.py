"""User models and schemas."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr = Field(description="User email address")
    username: str = Field(min_length=3, max_length=50, description="Username")
    full_name: str | None = Field(default=None, description="Full name")


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(min_length=8, description="User password")


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = Field(default=None, description="User email address")
    username: str | None = Field(default=None, min_length=3, max_length=50, description="Username")
    full_name: str | None = Field(default=None, description="Full name")
    is_active: bool | None = Field(default=None, description="Is user active")


class User(UserBase):
    """User response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="User ID")
    is_active: bool = Field(default=True, description="Is user active")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Last update timestamp",
    )


class UserInDB(User):
    """User schema with hashed password (internal use)."""

    hashed_password: str = Field(description="Hashed password")
