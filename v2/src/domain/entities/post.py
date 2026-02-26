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