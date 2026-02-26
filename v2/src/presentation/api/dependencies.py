from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.database.connection import get_db
from infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from infrastructure.repositories.sqlalchemy_post_repository import SQLAlchemyPostRepository
from application.use_cases.user.create_user import CreateUserUseCase
from application.use_cases.user.authenticate_user import AuthenticateUserUseCase
from application.use_cases.post.create_post import CreatePostUseCase
from infrastructure.security.password import PasswordHasher
from infrastructure.security.jwt_handler import JWTHandler


def get_user_repository(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


def get_post_repository(db: Session = Depends(get_db)) -> SQLAlchemyPostRepository:
    return SQLAlchemyPostRepository(db)


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_handler() -> JWTHandler:
    return JWTHandler()


def get_create_user_use_case(
    user_repo = Depends(get_user_repository),
    password_hasher = Depends(get_password_hasher)
) -> CreateUserUseCase:
    return CreateUserUseCase(user_repo, password_hasher)


def get_authenticate_user_use_case(
    user_repo = Depends(get_user_repository),
    password_hasher = Depends(get_password_hasher)
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(user_repo, password_hasher)


def get_create_post_use_case(
    post_repo = Depends(get_post_repository)
) -> CreatePostUseCase:
    return CreatePostUseCase(post_repo)