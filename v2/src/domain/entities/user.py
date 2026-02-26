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