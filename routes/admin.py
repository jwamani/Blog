from typing import Annotated

from fastapi import APIRouter, Depends, Path
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import delete
from starlette import status

from database import get_db
from .auth import get_current_user
from models import Post

admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@admin_router.get("/posts")
async def read_all_posts(db: db_dependency, current_user: user_dependency):
    if current_user is None or current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Authentication Failed")
    return db.query(Post).all()


@admin_router.delete("/posts", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all(db: db_dependency, user: user_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Authentication Failed")
    # return db.execute(delete(Post))
    db.query(Post).delete(synchronize_session=False)
    db.commit()

@admin_router.delete("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(db: db_dependency, user: user_dependency, post_id: int):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(post)
    db.commit()


