from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from starlette import status
import logging

from models import User
from schemas import UserPasswd, User as UserR, ResponseUser
from .auth import get_current_user
from database import get_db
from security import verify_password, gen_hash

logger = logging.getLogger(__name__)
user_router = APIRouter(prefix="/users", tags=["Users"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


def check_user(user: dict, db: Session, /) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated")
    user_d: Optional[User] = db.query(User).filter(User.id == user.get("id")).first()
    if user_d is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_d


@user_router.get("/", status_code=status.HTTP_200_OK, response_model=ResponseUser[UserR])
async def get_user(db: db_dependency, user: user_dependency):
    user_d = check_user(user, db)
    return {
        "data": user_d
    }


@user_router.put("/change")
async def change_password(db: db_dependency, user: user_dependency, updates: UserPasswd):
    # return updates.model_dump()["password"], user
    user_d = check_user(user, db)
    if verify_password(updates.password, user_d.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be the same as previous")
    setattr(user_d, "password_hash", gen_hash(updates.password))
    db.add(user_d)
    db.commit()
    logger.info(f"Password changed for user: {user_d.username}")
