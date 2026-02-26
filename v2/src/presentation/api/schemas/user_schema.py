from pydantic import BaseModel, Field
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=50)
    password: str = Field(..., min_length=8)
    phone_number: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, user):
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at
        )


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
        return cls(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            published=post.published,
            created_at=post.created_at
        )