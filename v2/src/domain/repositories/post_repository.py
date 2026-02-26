from abc import ABC, abstractmethod
from domain.entities.post import Post


class PostRepository(ABC):
    @abstractmethod
    async def create(self, post: Post) -> Post:
        pass

    @abstractmethod
    async def get_by_id(self, post_id: int) -> Post | None:
        pass

    @abstractmethod
    async def get_by_author_id(self, author_id: int) -> list[Post]:
        pass

    @abstractmethod
    async def update(self, post: Post) -> Post:
        pass

    @abstractmethod
    async def delete(self, post_id: int) -> bool:
        pass