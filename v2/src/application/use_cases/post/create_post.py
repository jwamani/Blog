from domain.entities.post import Post
from domain.repositories.post_repository import PostRepository


class CreatePostUseCase:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    async def execute(self, title: str, content: str, author_id: int) -> Post:
        # Business validation
        if len(title) < 5:
            raise ValueError("Title must be at least 5 characters")

        post = Post(
            id=None,
            title=title,
            content=content,
            author_id=author_id
        )
        return await self.post_repo.create(post)