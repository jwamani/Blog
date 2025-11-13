from fastapi import APIRouter, Depends
from starlette import status
from typing import Annotated
from sqlalchemy.orm import Session
import logging
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from datetime import timedelta

from security import gen_hash, authenticate_user, create_access_token, SECRET_KEY, ALGO
from schemas import UserCreate, Token
from models import User
from database import get_db

"""
During authentication / authorization:
login -> post request -> create jwt token
access protected routes -> pass and decode token -> obtain user info
"""

logger = logging.getLogger(__name__)

MINS = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)
db_dependency = Annotated[Session, Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


@auth_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, db: Annotated[Session, Depends(get_db)]):
    user: User = User(**user_create.model_dump(exclude={'password'}), password_hash=gen_hash(user_create.password))
    logger.debug(f"User with the following data: {user.role} ")
    db.add(user)
    db.commit()
    logger.info(f"User created: {user.username}")


@auth_router.post("/token", response_model=Token)
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db=db)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(user.username, user_id=user.id, user_role=user.role,
                                expires_delta=timedelta(MINS))
    logger.info(f"User authenticated: {form_data.username}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "success": True
    }


async def get_current_user(db: db_dependency, token: Annotated[str, Depends(oauth2_scheme)]):
    creds_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGO])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        user_role: str = payload.get("role")

        if username is None or user_id is None or user_role is None:
            raise creds_exception
        return {"username": username, "id": user_id, "role": user_role}
    except JWTError:
        raise creds_exception
