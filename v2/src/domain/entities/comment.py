from dataclasses import dataclass
from datetime import datetime


@dataclass
class Comment:
    id: int | None
    content: str
    user_id: int
    post_id: int
    created_at: datetime | None = None