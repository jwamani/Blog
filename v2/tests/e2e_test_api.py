import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from v2.src.infrastructure.database.connection import Base, get_db
from v2.src.infrastructure.security.password import PasswordHasher
from v2.src.infrastructure.security.jwt_handler import JWTHandler
from v2.src.main import app
from v2.src.domain.entities.user import User


# Create in-memory database for testing
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override get_db to use test database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create a test client with fresh test database."""
    # Create tables for this test
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    # Clean up tables after test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def auth_headers(client):
    """Create a test user and return auth headers."""
    # Register a test user
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # Login to get token
    response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuthEndpoints:
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"

    def test_register_short_password(self, client):
        """Test registration with short password - validation in Pydantic."""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "short"
            }
        )
        # Pydantic validation returns 422 for invalid request
        assert response.status_code == 422

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        # First registration
        response1 = client.post(
            "/auth/register",
            json={
                "username": "user1",
                "email": "duplicate@example.com",
                "password": "password123"
            }
        )
        assert response1.status_code == 200
        
        # Second registration with same email
        response2 = client.post(
            "/auth/register",
            json={
                "username": "user2",
                "email": "duplicate@example.com",
                "password": "password123"
            }
        )
        assert response2.status_code == 400


class TestPostEndpoints:
    def test_create_post_success(self, client, auth_headers):
        """Test successful post creation."""
        response = client.post(
            "/posts/",
            json={
                "title": "Test Post Title",
                "content": "This is a test post with sufficient content to pass validation",
                "published": True
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Post Title"


    def test_create_post_short_title(self, client, auth_headers):
        """Test post creation with short title."""
        response = client.post(
            "/posts/",
            json={
                "title": "Bad",
                "content": "This is a test post with sufficient content",
                "published": True
            },
            headers=auth_headers
        )
        assert response.status_code == 400
