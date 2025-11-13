from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_current_user
from database import get_db
from models import Post
from schemas import ResponsePostList, PostCreate, PostUpdate, PostResponse, ResponsePost

post_router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@post_router.get('/posts', status_code=status.HTTP_200_OK, response_model=ResponsePostList[PostResponse])
async def read_all_posts(db: db_dependency, current_user: user_dependency):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    posts = db.query(Post).filter(Post.user_id == current_user.get("id")).all()
    return {
        "status": "success",
        "data": posts,
        "results": len(posts)
    }

@post_router.get('/posts/{post_id}', status_code=status.HTTP_200_OK, response_model=ResponsePost[PostResponse])
async def read_single_post(db: db_dependency, current_user: user_dependency, post_id: int = Path(gt=0)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    post = db.query(Post).filter_by(user_id=current_user.get("id"), id=post_id).first()
    if post is not None:
        return {
            'data': post,
            'status': 'success'
        }
    raise HTTPException(status_code=404, detail="Post not found")


@post_router.post('/posts', status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)], current_user: user_dependency):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated")
    todo = Post(**post.model_dump(), user_id=current_user.get("id"))
    db.add(todo)
    db.commit()
    db.refresh(todo)


@post_router.put('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_post(db: db_dependency, post_update: PostUpdate,  current_user: user_dependency, post_id: int = Path(gt=0),):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated")
    # TODO: not completed update route
    post = db.query(Post).filter_by(id=post_id, user_id=current_user.get("id")).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    post_update = post_update.model_dump(exclude_unset=True)

    for k, v in post_update.items():
        setattr(post, k, v)

    db.add(post)
    db.commit()
    db.refresh(post)

@post_router.delete('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(db: db_dependency,  current_user: user_dependency, post_id: int = Path(gt=0)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated")
    post = db.query(Post).filter_by(id=post_id, user_id=current_user.get("id")).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()

