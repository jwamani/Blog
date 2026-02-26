from v2.src.domain.entities.user import User
from v2.src.domain.repositories.user_repository import UserRepository

class AuthenticateUserUseCase:
    def __init__(self, user_repo: UserRepository, password_verifier):
        self.user_repo = user_repo
        self.password_verifier = password_verifier

    async def execute(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise ValueError("Invalid credentials")

        if not user.is_active:
            raise ValueError("User account is inactive")

        if not self.password_verifier.verify(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        return user