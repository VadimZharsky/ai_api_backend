from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.models import LlmMessage


class ILlmClient(ABC):
    @abstractmethod
    async def send_chat_completion(self, messages: list[LlmMessage]) -> str:
        ...

    @abstractmethod
    def send_chat_completion_stream(self, messages: list[LlmMessage]) -> AsyncIterator[str]:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...
