from abc import ABC, abstractmethod


class Autobuyer(ABC):
    @abstractmethod
    async def start(
            self
    ) -> None:
        pass
