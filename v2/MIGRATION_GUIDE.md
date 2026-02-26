# Clean Architecture Migration Guide

## Overview
This guide provides practical dos and don'ts for migrating the FastAPI Blog project to clean architecture in the v2 folder.

---

## Table of Contents
1. [Core Principles](#core-principles)
2. [Migration Strategy](#migration-strategy)
3. [Layer-by-Layer Guide](#layer-by-layer-guide)
4. [Common Patterns](#common-patterns)
5. [Testing Strategy](#testing-strategy)

---

## Core Principles

### The Dependency Rule
**DO**: Always point dependencies inward (toward the domain)
```
Presentation → Application → Domain
Infrastructure → Application → Domain
```

**DON'T**: Never let inner layers depend on outer layers
```python
# ❌ WRONG: Domain depending on SQLAlchemy
from sqlalchemy import Column, Integer
class User:
    id = Column(Integer, primary_key=True)

# ✅ CORRECT: Pure domain entity
from dataclasses import dataclass
@dataclass
class User:
    id: int | None
    username: str
    email: str
```

---

## Migration Strategy

### Phase 1: Domain Layer (Start Here)
Extract business entities and define repository interfaces.

**DO**: Start with one entity at a time
```python
# v2/domain/entities/post.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Post:
    id: int | None
    title: str
    content: str
    author_id: int
    published: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
```

**DON'T**: Copy SQLAlchemy models directly
```python
# ❌ WRONG: Bringing ORM into domain
from sqlalchemy.orm import relationship
class Post:
    author = relationship("User", back_populates="posts")
```

### Phase 2: Application Layer
Create use cases that orchestrate business logic.

**DO**: One use case per action
```python
# v2/application/use_cases/post/create_post.py
from domain.entities.post import Post
from domain.repositories.post_repository import PostRepository

class CreatePostUseCase:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    async def execute(self, title: str, content: str, author_id: int) -> Post:
        # Business validation
        if len(title) < 5:
            raise ValueError("Title must be at least 5 characters")

        post = Post(
            id=None,
            title=title,
            content=content,
            author_id=author_id
        )
        return await self.post_repo.create(post)
```

**DON'T**: Put database queries in use cases
```python
# ❌ WRONG: Direct database access in use case
class CreatePostUseCase:
    def __init__(self, db: Session):
        self.db = db

    async def execute(self, title: str, content: str):
        post = PostModel(title=title, content=content)  # SQLAlchemy model
        self.db.add(post)
        self.db.commit()
```

### Phase 3: Infrastructure Layer
Implement concrete repositories and database connections.

**DO**: Implement repository interfaces
```python
# v2/infrastructure/repositories/sqlalchemy_post_repository.py
from sqlalchemy.orm import Session
from domain.entities.post import Post
from domain.repositories.post_repository import PostRepository
from infrastructure.database.models import PostModel

class SQLAlchemyPostRepository(PostRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create(self, post: Post) -> Post:
        db_post = PostModel(
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            published=post.published
        )
        self.db.add(db_post)
        self.db.commit()
        self.db.refresh(db_post)

        # Convert back to domain entity
        return Post(
            id=db_post.id,
            title=db_post.title,
            content=db_post.content,
            author_id=db_post.author_id,
            published=db_post.published,
            created_at=db_post.created_at
        )
```

**DON'T**: Return ORM models from repositories
```python
# ❌ WRONG: Returning SQLAlchemy model
async def create(self, post: Post) -> PostModel:  # Should return Post entity
    db_post = PostModel(...)
    self.db.add(db_post)
    return db_post  # Leaking infrastructure to application layer
```

### Phase 4: Presentation Layer
Build API routes that use use cases.

**DO**: Inject dependencies properly
```python
# v2/presentation/api/routes/posts.py
from fastapi import APIRouter, Depends
from presentation.api.dependencies import get_create_post_use_case
from presentation.api.schemas.post_schema import PostCreate, PostResponse

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    use_case: CreatePostUseCase = Depends(get_create_post_use_case)
):
    post = await use_case.execute(
        title=post_data.title,
        content=post_data.content,
        author_id=post_data.author_id
    )
    return PostResponse.from_entity(post)
```

**DON'T**: Put business logic in routes
```python
# ❌ WRONG: Business logic in API route
@router.post("/")
async def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    if len(post_data.title) < 5:  # Business rule in presentation layer
        raise HTTPException(400, "Title too short")

    db_post = PostModel(title=post_data.title, content=post_data.content)
    db.add(db_post)
    db.commit()
```

---

## Layer-by-Layer Guide

### Domain Layer

#### Entities
**DO**: Keep entities pure and framework-agnostic
```python
# v2/domain/entities/user.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int | None
    username: str
    email: str
    hashed_password: str
    phone_number: str | None = None
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime | None = None
```

**DON'T**: Add framework-specific annotations
```python
# ❌ WRONG
from pydantic import BaseModel, EmailStr

class User(BaseModel):  # Pydantic belongs in presentation layer
    email: EmailStr
```

#### Repository Interfaces
**DO**: Define abstract contracts
```python
# v2/domain/repositories/user_repository.py
from abc import ABC, abstractmethod
from domain.entities.user import User

class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        pass
```

**DON'T**: Include implementation details
```python
# ❌ WRONG: SQLAlchemy in interface
from sqlalchemy.orm import Session

class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User, db: Session) -> User:  # Session is implementation detail
        pass
```

---

### Application Layer

#### Use Cases
**DO**: Single responsibility per use case
```python
# v2/application/use_cases/user/authenticate_user.py
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository

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
```

**DON'T**: Mix multiple responsibilities
```python
# ❌ WRONG: Doing too much in one use case
class UserManagementUseCase:
    async def create_user(self, ...): pass
    async def update_user(self, ...): pass
    async def delete_user(self, ...): pass
    async def authenticate_user(self, ...): pass  # Split these into separate use cases
```

#### DTOs (Data Transfer Objects)
**DO**: Use DTOs for cross-layer communication when needed
```python
# v2/application/dtos/post_dto.py
from dataclasses import dataclass

@dataclass
class CreatePostDTO:
    title: str
    content: str
    author_id: int
    published: bool = True
```

**DON'T**: Use DTOs if entities suffice
```python
# ❌ UNNECESSARY: If entity already fits, just use it
@dataclass
class PostDTO:  # Just use Post entity directly
    id: int
    title: str
    content: str
```

---

### Infrastructure Layer

#### Database Models
**DO**: Keep ORM models separate from entities
```python
# v2/infrastructure/database/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from infrastructure.database.connection import Base

class PostModel(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("UserModel", back_populates="posts")
```

**DON'T**: Use the same class for domain and database
```python
# ❌ WRONG: Mixing concerns
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):  # Domain entity shouldn't be ORM model
    __tablename__ = "posts"
```

#### Repository Implementation
**DO**: Convert between ORM models and entities
```python
# v2/infrastructure/repositories/sqlalchemy_user_repository.py
from sqlalchemy.orm import Session
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.database.models import UserModel

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()

        if not db_user:
            return None

        return self._to_entity(db_user)

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

    def _to_model(self, user: User) -> UserModel:
        """Convert domain entity to ORM model"""
        return UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            phone_number=user.phone_number,
            is_active=user.is_active,
            is_admin=user.is_admin
        )
```

---

### Presentation Layer

#### API Schemas (Pydantic)
**DO**: Define request/response schemas
```python
# v2/presentation/api/schemas/post_schema.py
from pydantic import BaseModel, Field
from datetime import datetime

class PostCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10)
    published: bool = True

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    published: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, post):
        """Convert domain entity to API response"""
        return cls(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            published=post.published,
            created_at=post.created_at
        )
```

**DON'T**: Use entities directly in API
```python
# ❌ WRONG: Exposing domain entity
from domain.entities.post import Post

@router.get("/posts/{id}", response_model=Post)  # Don't expose entity
async def get_post(id: int):
    pass
```

#### Dependencies
**DO**: Use FastAPI dependencies for injection
```python
# v2/presentation/api/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.database.connection import get_db
from infrastructure.repositories.sqlalchemy_post_repository import SQLAlchemyPostRepository
from infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from application.use_cases.post.create_post import CreatePostUseCase
from application.use_cases.user.authenticate_user import AuthenticateUserUseCase
from infrastructure.security.password import PasswordHasher
from infrastructure.security.jwt_handler import JWTHandler

def get_post_repository(db: Session = Depends(get_db)) -> SQLAlchemyPostRepository:
    return SQLAlchemyPostRepository(db)

def get_user_repository(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)

def get_create_post_use_case(
    repo = Depends(get_post_repository)
) -> CreatePostUseCase:
    return CreatePostUseCase(repo)

def get_authenticate_user_use_case(
    user_repo = Depends(get_user_repository)
) -> AuthenticateUserUseCase:
    password_verifier = PasswordHasher()
    return AuthenticateUserUseCase(user_repo, password_verifier)
```

---

## Common Patterns

### Pattern 1: CRUD Operations

**Migrating from old structure:**
```python
# OLD: routes/posts.py
@router.post("/posts")
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()
    return db_post
```

**New clean architecture:**
```python
# NEW: v2/presentation/api/routes/posts.py
@router.post("/posts")
async def create_post(
    post_data: PostCreate,
    use_case: CreatePostUseCase = Depends(get_create_post_use_case),
    current_user = Depends(get_current_user)  # From auth dependency
):
    post = await use_case.execute(
        title=post_data.title,
        content=post_data.content,
        author_id=current_user.id
    )
    return PostResponse.from_entity(post)
```

### Pattern 2: Authentication

**DO**: Separate password hashing from business logic
```python
# v2/infrastructure/security/password.py
from passlib.context import CryptContext

class PasswordHasher:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
```

```python
# v2/infrastructure/security/jwt_handler.py
from datetime import datetime, timedelta
from jose import jwt
from config import settings

class JWTHandler:
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
```

### Pattern 3: File Uploads

**DO**: Handle file operations in infrastructure
```python
# v2/infrastructure/storage/file_storage.py
from pathlib import Path
import shutil

class FileStorage:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

    async def save_file(self, file, filename: str) -> str:
        file_path = self.upload_dir / filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return str(file_path)
```

```python
# v2/application/use_cases/post/upload_image.py
class UploadPostImageUseCase:
    def __init__(self, file_storage: FileStorage, post_repo: PostRepository):
        self.file_storage = file_storage
        self.post_repo = post_repo

    async def execute(self, post_id: int, file) -> str:
        # Validate file type, size, etc.
        filename = f"post_{post_id}_{file.filename}"
        file_path = await self.file_storage.save_file(file, filename)

        # Update post with image path
        post = await self.post_repo.get_by_id(post_id)
        post.image_path = file_path
        await self.post_repo.update(post)

        return file_path
```

---

## Testing Strategy

### Unit Testing Domain & Application

**DO**: Test use cases without database
```python
# test/unit/test_create_post_use_case.py
import pytest
from unittest.mock import AsyncMock
from application.use_cases.post.create_post import CreatePostUseCase
from domain.entities.post import Post

@pytest.mark.asyncio
async def test_create_post_success():
    # Mock repository
    mock_repo = AsyncMock()
    mock_repo.create.return_value = Post(
        id=1,
        title="Test Post",
        content="Test Content",
        author_id=1
    )

    # Test use case
    use_case = CreatePostUseCase(mock_repo)
    result = await use_case.execute("Test Post", "Test Content", 1)

    assert result.id == 1
    assert result.title == "Test Post"
    mock_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_post_title_too_short():
    mock_repo = AsyncMock()
    use_case = CreatePostUseCase(mock_repo)

    with pytest.raises(ValueError, match="Title must be at least 5 characters"):
        await use_case.execute("Hi", "Content", 1)
```

### Integration Testing Infrastructure

**DO**: Test repository implementations with real database
```python
# test/integration/test_post_repository.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.database.models import Base, PostModel
from infrastructure.repositories.sqlalchemy_post_repository import SQLAlchemyPostRepository
from domain.entities.post import Post

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.mark.asyncio
async def test_create_post_repository(db_session):
    repo = SQLAlchemyPostRepository(db_session)

    post = Post(
        id=None,
        title="Integration Test",
        content="Testing repository",
        author_id=1
    )

    created_post = await repo.create(post)

    assert created_post.id is not None
    assert created_post.title == "Integration Test"
```

### E2E Testing API

**DO**: Test complete flows
```python
# test/e2e/test_posts_api.py
from fastapi.testclient import TestClient
from v2.main import app

client = TestClient(app)

def test_create_post_endpoint():
    # Create user and get token first
    auth_response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "testpass"
    })
    token = auth_response.json()["access_token"]

    # Create post
    response = client.post(
        "/posts",
        json={
            "title": "E2E Test Post",
            "content": "Testing end-to-end",
            "published": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "E2E Test Post"
```

---

## Migration Checklist

### Before Starting
- [ ] Read this guide completely
- [ ] Understand current codebase structure
- [ ] Set up v2 folder structure
- [ ] Decide which feature to migrate first (start small)

### Per Feature Migration
- [ ] Extract domain entities from models.py
- [ ] Define repository interfaces in domain
- [ ] Create use cases in application layer
- [ ] Implement repositories in infrastructure
- [ ] Create API schemas in presentation
- [ ] Build routes using use cases
- [ ] Write unit tests for use cases
- [ ] Write integration tests for repositories
- [ ] Write E2E tests for API endpoints

### After Each Feature
- [ ] Run all tests
- [ ] Check no cross-layer violations
- [ ] Update documentation
- [ ] Code review

---

## Common Mistakes to Avoid

1. **❌ Skipping repository interfaces** - Always define abstract interfaces first
2. **❌ Returning ORM models from repositories** - Always convert to entities
3. **❌ Business logic in routes** - Move to use cases
4. **❌ Direct database access in use cases** - Use repository interfaces
5. **❌ Mixing layers** - Respect the dependency rule
6. **❌ Over-engineering** - Start simple, refactor as needed
7. **❌ No tests** - Write tests for each layer
8. **❌ Forgetting error handling** - Handle exceptions at each layer appropriately

---

## Resources

### Project Structure Reference
See the main directory tree in `v2/` for the complete structure.

### Existing Code to Reference
- Current models: `/models.py`
- Current routes: `/routes/`
- Current schemas: `/schemas.py`
- Current security: `/security.py`

### Next Steps
1. Start with User entity (most fundamental)
2. Then migrate authentication flow
3. Follow with Post entity
4. Finally migrate admin features

Good luck with the migration! 🚀
