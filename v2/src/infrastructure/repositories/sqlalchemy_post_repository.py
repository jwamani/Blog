from sqlalchemy.orm import Session
from domain.entities.post import Post
from domain.repositories.post_repository import PostRepository
from infrastructure.database.models import PostModel


class SQLAlchemyPostRepository(PostRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create(self, post: Post) -> Post:
        db_post = PostModel(
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            published=post.published
        )
        self.db.add(db_post)
        self.db.commit()
        self.db.refresh(db_post)

        return Post(
            id=db_post.id,
            title=db_post.title,
            content=db_post.content,
            author_id=db_post.author_id,
            published=db_post.published,
            created_at=db_post.created_at,
            updated_at=db_post.updated_at
        )

    async def get_by_id(self, post_id: int) -> Post | None:
        db_post = self.db.query(PostModel).filter(PostModel.id == post_id).first()
        if not db_post:
            return None
        return self._to_entity(db_post)

    async def get_by_author_id(self, author_id: int) -> list[Post]:
        db_posts = self.db.query(PostModel).filter(PostModel.author_id == author_id).all()
        return [self._to_entity(db_post) for db_post in db_posts]

    async def update(self, post: Post) -> Post:
        db_post = self.db.query(PostModel).filter(PostModel.id == post.id).first()
        if not db_post:
            raise ValueError("Post not found")
        db_post.title = post.title
        db_post.content = post.content
        db_post.published = post.published
        self.db.commit()
        self.db.refresh(db_post)
        return self._to_entity(db_post)

    async def delete(self, post_id: int) -> bool:
        db_post = self.db.query(PostModel).filter(PostModel.id == post_id).first()
        if not db_post:
            return False
        self.db.delete(db_post)
        self.db.commit()
        return True

    def _to_entity(self, db_post: PostModel) -> Post:
        return Post(
            id=db_post.id,
            title=db_post.title,
            content=db_post.content,
            author_id=db_post.author_id,
            published=db_post.published,
            created_at=db_post.created_at,
            updated_at=db_post.updated_at
        )