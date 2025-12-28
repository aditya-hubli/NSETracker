"""Tests for User Service API endpoints."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from services.user_service.main import app
from shared.exceptions import NotFoundError

client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self) -> None:
        """Test health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "user-service"


class TestCreateUser:
    """Tests for user creation endpoint."""

    @patch("services.user_service.routes.user_repository")
    def test_create_user_success(self, mock_repo: AsyncMock) -> None:
        """Test successful user creation."""
        user_id = str(uuid4())
        mock_repo.get_by_email = AsyncMock(return_value=None)
        mock_repo.create = AsyncMock(
            return_value={
                "id": user_id,
                "email": "test@example.com",
                "username": "testuser",
                "full_name": "Test User",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        )

        response = client.post(
            "/api/v1/users/",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "full_name": "Test User",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "id" in data

    @patch("services.user_service.routes.user_repository")
    def test_create_user_email_exists(self, mock_repo: AsyncMock) -> None:
        """Test user creation fails when email already exists."""
        mock_repo.get_by_email = AsyncMock(
            return_value={"id": str(uuid4()), "email": "test@example.com"}
        )

        response = client.post(
            "/api/v1/users/",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]

    def test_create_user_invalid_email(self) -> None:
        """Test user creation fails with invalid email."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "invalid-email",
                "username": "testuser",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 422

    def test_create_user_short_password(self) -> None:
        """Test user creation fails with short password."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "short",
            },
        )

        assert response.status_code == 422

    def test_create_user_short_username(self) -> None:
        """Test user creation fails with short username."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "test@example.com",
                "username": "ab",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 422


class TestGetUser:
    """Tests for get user endpoint."""

    @patch("services.user_service.routes.user_repository")
    def test_get_user_success(self, mock_repo: AsyncMock) -> None:
        """Test successful user retrieval."""
        user_id = uuid4()
        mock_repo.get_by_id = AsyncMock(
            return_value={
                "id": str(user_id),
                "email": "test@example.com",
                "username": "testuser",
                "full_name": "Test User",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        )

        response = client.get(f"/api/v1/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    @patch("services.user_service.routes.user_repository")
    def test_get_user_not_found(self, mock_repo: AsyncMock) -> None:
        """Test get user returns 404 when not found."""
        user_id = uuid4()
        mock_repo.get_by_id = AsyncMock(
            side_effect=NotFoundError(resource="User", resource_id=str(user_id))
        )

        response = client.get(f"/api/v1/users/{user_id}")

        assert response.status_code == 404

    def test_get_user_invalid_uuid(self) -> None:
        """Test get user returns 422 for invalid UUID."""
        response = client.get("/api/v1/users/invalid-uuid")

        assert response.status_code == 422


class TestListUsers:
    """Tests for list users endpoint."""

    @patch("services.user_service.routes.user_repository")
    def test_list_users_success(self, mock_repo: AsyncMock) -> None:
        """Test successful user listing."""
        mock_repo.get_all = AsyncMock(
            return_value=[
                {
                    "id": str(uuid4()),
                    "email": "user1@example.com",
                    "username": "user1",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
                {
                    "id": str(uuid4()),
                    "email": "user2@example.com",
                    "username": "user2",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
            ]
        )

        response = client.get("/api/v1/users/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @patch("services.user_service.routes.user_repository")
    def test_list_users_empty(self, mock_repo: AsyncMock) -> None:
        """Test list users returns empty list."""
        mock_repo.get_all = AsyncMock(return_value=[])

        response = client.get("/api/v1/users/")

        assert response.status_code == 200
        assert response.json() == []

    @patch("services.user_service.routes.user_repository")
    def test_list_users_pagination(self, mock_repo: AsyncMock) -> None:
        """Test list users with pagination."""
        mock_repo.get_all = AsyncMock(return_value=[])

        response = client.get("/api/v1/users/?skip=10&limit=5")

        assert response.status_code == 200
        mock_repo.get_all.assert_called_once_with(skip=10, limit=5)


class TestUpdateUser:
    """Tests for update user endpoint."""

    @patch("services.user_service.routes.user_repository")
    def test_update_user_success(self, mock_repo: AsyncMock) -> None:
        """Test successful user update."""
        user_id = uuid4()
        mock_repo.update = AsyncMock(
            return_value={
                "id": str(user_id),
                "email": "updated@example.com",
                "username": "updateduser",
                "full_name": "Updated User",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            }
        )

        response = client.put(
            f"/api/v1/users/{user_id}",
            json={"email": "updated@example.com", "username": "updateduser"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"

    @patch("services.user_service.routes.user_repository")
    def test_update_user_not_found(self, mock_repo: AsyncMock) -> None:
        """Test update user returns 404 when not found."""
        user_id = uuid4()
        mock_repo.update = AsyncMock(
            side_effect=NotFoundError(resource="User", resource_id=str(user_id))
        )

        response = client.put(
            f"/api/v1/users/{user_id}",
            json={"email": "updated@example.com"},
        )

        assert response.status_code == 404

    def test_update_user_no_fields(self) -> None:
        """Test update user fails with no fields to update."""
        user_id = uuid4()

        response = client.put(
            f"/api/v1/users/{user_id}",
            json={},
        )

        assert response.status_code == 400
        assert "No fields to update" in response.json()["detail"]


class TestDeleteUser:
    """Tests for delete user endpoint."""

    @patch("services.user_service.routes.user_repository")
    def test_delete_user_success(self, mock_repo: AsyncMock) -> None:
        """Test successful user deletion."""
        user_id = uuid4()
        mock_repo.get_by_id = AsyncMock(
            return_value={
                "id": str(user_id),
                "email": "test@example.com",
                "username": "testuser",
            }
        )
        mock_repo.delete = AsyncMock(return_value=True)

        response = client.delete(f"/api/v1/users/{user_id}")

        assert response.status_code == 204

    @patch("services.user_service.routes.user_repository")
    def test_delete_user_not_found(self, mock_repo: AsyncMock) -> None:
        """Test delete user returns 404 when not found."""
        user_id = uuid4()
        mock_repo.get_by_id = AsyncMock(
            side_effect=NotFoundError(resource="User", resource_id=str(user_id))
        )

        response = client.delete(f"/api/v1/users/{user_id}")

        assert response.status_code == 404
