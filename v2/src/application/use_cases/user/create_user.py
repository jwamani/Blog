from domain.entities.user import User
from domain.repositories.user_repository import UserRepository


class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository, password_hasher):
        self.user_repo = user_repo
        self.password_hasher = password_hasher

    async def execute(self, username: str, email: str, password: str, phone_number: str | None = None) -> User:
        # Business validation
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Check if email already exists
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")

        hashed_password = self.password_hasher.hash(password)

        user = User(
            id=None,
            username=username,
            email=email,
            hashed_password=hashed_password,
            phone_number=phone_number
        )
        return await self.user_repo.create(user)