from fastapi import APIRouter, Depends, HTTPException
from presentation.api.dependencies import get_create_post_use_case
from presentation.api.schemas.post_schema import PostCreate, PostResponse
from application.use_cases.post.create_post import CreatePostUseCase

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    use_case: CreatePostUseCase = Depends(get_create_post_use_case)
):
    try:
        post = await use_case.execute(
            title=post_data.title,
            content=post_data.content,
            author_id=1  # TODO: Get from auth
        )
        return PostResponse.from_entity(post)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))