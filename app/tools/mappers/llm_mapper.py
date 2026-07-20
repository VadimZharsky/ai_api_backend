from app.db import Message
from app.models import LlmMessage, MessageRoleType


class LlmMapper:
    @staticmethod
    def build_messages_for_llm(
            history: list[Message], system_prompt: str | None = None
    ) -> list[LlmMessage]:
        messages: list[LlmMessage] = []
        if system_prompt is not None:
            messages.append(LlmMessage(role=MessageRoleType.SYSTEM, content=system_prompt))
        for msg in history:
            match msg.role:
                case MessageRoleType.USER:
                    messages.append(
                        LlmMessage(role=MessageRoleType.USER, content=msg.content)
                    )
                case MessageRoleType.ASSISTANT:
                    messages.append(
                        LlmMessage(role=MessageRoleType.ASSISTANT, content=msg.content)
                    )
                case _:
                    continue
        return messages
