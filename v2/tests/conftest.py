
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from v2.src.infrastructure.database.connection import Base
from v2.src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from v2.src.infrastructure.repositories.sqlalchemy_post_repository import SQLAlchemyPostRepository
from v2.src.infrastructure.security.password import PasswordHasher


@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def user_repo(test_db):
    """Provide a user repository with test database."""
    return SQLAlchemyUserRepository(test_db)


@pytest.fixture
def post_repo(test_db):
    """Provide a post repository with test database."""
    return SQLAlchemyPostRepository(test_db)


@pytest.fixture
def password_hasher():
    """Provide a password hasher."""
    return PasswordHasher()
