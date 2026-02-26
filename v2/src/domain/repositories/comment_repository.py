from abc import ABC, abstractmethod
from domain.entities.comment import Comment


class CommentRepository(ABC):
    @abstractmethod
    async def create(self, comment: Comment) -> Comment:
        pass

    @abstractmethod
    async def get_by_id(self, comment_id: int) -> Comment | None:
        pass

    @abstractmethod
    async def get_by_post_id(self, post_id: int) -> list[Comment]:
        pass

    @abstractmethod
    async def update(self, comment: Comment) -> Comment:
        pass

    @abstractmethod
    async def delete(self, comment_id: int) -> bool:
        pass