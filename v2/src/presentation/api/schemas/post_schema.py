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
        return cls(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            published=post.published,
            created_at=post.created_at
        )