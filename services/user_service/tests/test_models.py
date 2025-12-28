"""Tests for User models."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.user_service.models import User, UserCreate, UserUpdate


class TestUserCreate:
    """Tests for UserCreate model."""

    def test_valid_user_create(self) -> None:
        """Test valid user creation data."""
        user = UserCreate(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="securepassword123",
        )
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.password == "securepassword123"

    def test_user_create_without_full_name(self) -> None:
        """Test user creation without full name."""
        user = UserCreate(
            email="test@example.com",
            username="testuser",
            password="securepassword123",
        )
        assert user.full_name is None

    def test_user_create_invalid_email(self) -> None:
        """Test user creation fails with invalid email."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="invalid-email",
                username="testuser",
                password="securepassword123",
            )

    def test_user_create_short_username(self) -> None:
        """Test user creation fails with short username."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="ab",
                password="securepassword123",
            )

    def test_user_create_long_username(self) -> None:
        """Test user creation fails with long username."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="a" * 51,
                password="securepassword123",
            )

    def test_user_create_short_password(self) -> None:
        """Test user creation fails with short password."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="testuser",
                password="short",
            )


class TestUserUpdate:
    """Tests for UserUpdate model."""

    def test_valid_user_update(self) -> None:
        """Test valid user update data."""
        update = UserUpdate(
            email="updated@example.com",
            username="updateduser",
        )
        assert update.email == "updated@example.com"
        assert update.username == "updateduser"

    def test_user_update_partial(self) -> None:
        """Test partial user update."""
        update = UserUpdate(email="updated@example.com")
        assert update.email == "updated@example.com"
        assert update.username is None
        assert update.full_name is None
        assert update.is_active is None

    def test_user_update_empty(self) -> None:
        """Test empty user update is valid."""
        update = UserUpdate()
        assert update.email is None
        assert update.username is None

    def test_user_update_invalid_email(self) -> None:
        """Test user update fails with invalid email."""
        with pytest.raises(ValidationError):
            UserUpdate(email="invalid-email")


class TestUser:
    """Tests for User model."""

    def test_user_from_dict(self) -> None:
        """Test creating User from dictionary."""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
        )
        assert user.id == user_id
        assert user.email == "test@example.com"
        assert user.is_active is True

    def test_user_defaults(self) -> None:
        """Test User default values."""
        user = User(
            email="test@example.com",
            username="testuser",
        )
        assert user.id is not None
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.full_name is None
