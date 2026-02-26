from sqlalchemy.orm import Session
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create(self, user: User) -> User:
        db_user = UserModel(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            phone_number=user.phone_number,
            is_active=user.is_active,
            is_admin=user.is_admin
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        # Convert back to domain entity
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            phone_number=db_user.phone_number,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            created_at=db_user.created_at
        )

    async def get_by_id(self, user_id: int) -> User | None:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None
        return self._to_entity(db_user)

    async def get_by_email(self, email: str) -> User | None:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if not db_user:
            return None
        return self._to_entity(db_user)

    async def update(self, user: User) -> User:
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if not db_user:
            raise ValueError("User not found")
        db_user.username = user.username
        db_user.email = user.email
        db_user.hashed_password = user.hashed_password
        db_user.phone_number = user.phone_number
        db_user.is_active = user.is_active
        db_user.is_admin = user.is_admin
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_entity(db_user)

    async def delete(self, user_id: int) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return False
        self.db.delete(db_user)
        self.db.commit()
        return True

    def _to_entity(self, db_user: UserModel) -> User:
        """Convert ORM model to domain entity"""
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            phone_number=db_user.phone_number,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            created_at=db_user.created_at
        )