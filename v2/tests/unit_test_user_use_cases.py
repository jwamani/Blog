import pytest
from unittest.mock import AsyncMock

from v2.src.domain.entities.user import User
from v2.src.application.use_cases.user.create_user import CreateUserUseCase
from v2.src.application.use_cases.user.authenticate_user import AuthenticateUserUseCase


@pytest.mark.asyncio
class TestCreateUserUseCase:
    async def test_create_user_success(self, password_hasher):
        """Test successful user creation."""
        # Mock repository
        mock_repo = AsyncMock()
        mock_repo.get_by_email.return_value = None
        
        def capture_user(user):
            return User(
                id=1,
                username=user.username,
                email=user.email,
                hashed_password=user.hashed_password,
                phone_number=user.phone_number,
                is_active=user.is_active,
                is_admin=user.is_admin,
                created_at=None
            )
        
        mock_repo.create.side_effect = capture_user

        use_case = CreateUserUseCase(mock_repo, password_hasher)
        user = await use_case.execute("john", "john@example.com", "password123")

        assert user.id == 1
        assert user.username == "john"
        assert user.email == "john@example.com"
        mock_repo.create.assert_called_once()

    async def test_create_user_username_too_short(self, password_hasher):
        """Test validation: username must be at least 3 characters."""
        mock_repo = AsyncMock()
        use_case = CreateUserUseCase(mock_repo, password_hasher)

        with pytest.raises(ValueError, match="Username must be at least 3 characters"):
            await use_case.execute("ab", "john@example.com", "password123")

    async def test_create_user_password_too_short(self, password_hasher):
        """Test validation: password must be at least 8 characters."""
        mock_repo = AsyncMock()
        use_case = CreateUserUseCase(mock_repo, password_hasher)

        with pytest.raises(ValueError, match="Password must be at least 8 characters"):
            await use_case.execute("john", "john@example.com", "short")

    async def test_create_user_email_already_exists(self, password_hasher):
        """Test validation: email must not already be registered."""
        mock_repo = AsyncMock()
        existing_user = User(
            id=1,
            username="existing",
            email="john@example.com",
            hashed_password="hash",
            is_active=True,
            is_admin=False
        )
        mock_repo.get_by_email.return_value = existing_user

        use_case = CreateUserUseCase(mock_repo, password_hasher)

        with pytest.raises(ValueError, match="Email already registered"):
            await use_case.execute("john", "john@example.com", "password123")


@pytest.mark.asyncio
class TestAuthenticateUserUseCase:
    async def test_authenticate_user_success(self, password_hasher):
        """Test successful user authentication."""
        hashed_password = password_hasher.hash("password123")
        mock_repo = AsyncMock()
        mock_user = User(
            id=1,
            username="john",
            email="john@example.com",
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False
        )
        mock_repo.get_by_email.return_value = mock_user

        use_case = AuthenticateUserUseCase(mock_repo, password_hasher)
        user = await use_case.execute("john@example.com", "password123")

        assert user.id == 1
        assert user.email == "john@example.com"

    async def test_authenticate_user_not_found(self, password_hasher):
        """Test authentication: user not found."""
        mock_repo = AsyncMock()
        mock_repo.get_by_email.return_value = None

        use_case = AuthenticateUserUseCase(mock_repo, password_hasher)

        with pytest.raises(ValueError, match="Invalid credentials"):
            await use_case.execute("nonexistent@example.com", "password123")

    async def test_authenticate_user_inactive(self, password_hasher):
        """Test authentication: user account is inactive."""
        hashed_password = password_hasher.hash("password123")
        mock_repo = AsyncMock()
        mock_user = User(
            id=1,
            username="john",
            email="john@example.com",
            hashed_password=hashed_password,
            is_active=False,
            is_admin=False
        )
        mock_repo.get_by_email.return_value = mock_user

        use_case = AuthenticateUserUseCase(mock_repo, password_hasher)

        with pytest.raises(ValueError, match="User account is inactive"):
            await use_case.execute("john@example.com", "password123")

    async def test_authenticate_user_wrong_password(self, password_hasher):
        """Test authentication: wrong password."""
        hashed_password = password_hasher.hash("password123")
        mock_repo = AsyncMock()
        mock_user = User(
            id=1,
            username="john",
            email="john@example.com",
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False
        )
        mock_repo.get_by_email.return_value = mock_user

        use_case = AuthenticateUserUseCase(mock_repo, password_hasher)

        with pytest.raises(ValueError, match="Invalid credentials"):
            await use_case.execute("john@example.com", "wrongpassword")
