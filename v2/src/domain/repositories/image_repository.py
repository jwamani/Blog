from abc import ABC, abstractmethod
from v2.src.domain.entities.image import Image


class ImageRepository(ABC):
    @abstractmethod
    async def create(self, image: Image) -> Image:
        pass

    @abstractmethod
    async def get_by_id(self, image_id: int) -> Image | None:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> list[Image]:
        pass

    @abstractmethod
    async def delete(self, image_id: int) -> bool:
        pass