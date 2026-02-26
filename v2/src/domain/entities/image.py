from dataclasses import dataclass
from datetime import datetime


@dataclass
class Image:
    id: int | None
    filename: str
    file_path: str
    content_type: str
    file_size: int
    user_id: int
    uploaded_at: datetime | None = None