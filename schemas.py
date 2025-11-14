from datetime import datetime
from typing import Optional, Generic, TypeVar, Literal

from pydantic import BaseModel, Field


class PostBase(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PostCreate(PostBase):
    title: str = Field(min_length=5, max_length=50)
    content: str = Field(max_length=1000)
    user_id: int = Field(gt=0)


class PostUpdate(PostBase):
    title: Optional[str] = Field(min_length=5, max_length=50, default=None)
    content: Optional[str] = Field(max_length=1000, default=None)


class PostResponse(PostBase):
    id: int
    title: str
    content: str
    user_id: int
    created_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A holiday",
                "content": "Bought my first summer B-tree"
            }
        },
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + 'Z' if dt else None
            # modifies the datetime object to be timezone aware
        }
    }


T = TypeVar('T')


class ResponsePost(BaseModel, Generic[T]):
    data: T
    status: Literal['success', 'failure']


class ResponsePostList(BaseModel, Generic[T]):
    data: list[T]
    results: int
    status: Literal['success', 'failure']


class UserBase(BaseModel):
    id: Optional[int] = None
    fullname: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    role: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "fullname": "John Doe",
                "username": "johndoe",
                "email": "johndoe@mail.com",
                "password": "12345678",
                "role": "user"
            }
        }
    }


class Token(BaseModel):
    access_token: str
    token_type: str
    success: bool


class UserCreate(UserBase):
    fullname: str = Field(max_length=50)
    username: str = Field(max_length=30)
    email: str = Field(max_length=50, min_length=10)
    is_active: bool = Field(default=True)
    password: str = Field(min_length=8)
    role: str = Field(default='user')


class UserPasswd(UserBase):
    password: str = Field(min_length=8)


class User(BaseModel):
    id: int
    fullname: str
    username: str
    email: str
    is_active: bool
    role: str

class ResponseUser(BaseModel, Generic[T]):
    data: T