from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from starlette import status
import logging

from models import User
from schemas import User as UserR, ResponseUser, PasswordChange
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
    db_user: Optional[User] = db.query(User).filter(User.id == user.get("id")).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@user_router.get("/", status_code=status.HTTP_200_OK, response_model=ResponseUser[UserR])
async def get_user(db: db_dependency, user: user_dependency):
    user_d = check_user(user, db)
    return {
        "data": user_d
    }


@user_router.put("/change", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: db_dependency, user: user_dependency, updates: PasswordChange):
    # return updates.model_dump()["password"], user
    user_d = check_user(user, db)
    if verify_password(updates.old_password, user_d.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")

    if verify_password(updates.new_password, user_d.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be the same as the old password")
    user_d.password_hash = gen_hash(updates.password)
    db.add(user_d)
    db.commit()
    logger.info(f"Password changed for user: {user_d.username}")
