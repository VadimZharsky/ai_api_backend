from app.db import Chat, Message
from app.models import ChatHistoryResponse, MessageInfoResponse


class ChatMapper:
    @staticmethod
    def db_chat_to_chat_history_info(chat: Chat) -> ChatHistoryResponse:
        messages = [ChatMapper.db_message_to_message_info(m) for m in chat.messages]
        messages.sort(key=lambda m: m.id)
        return ChatHistoryResponse(
            id=chat.id,
            title=chat.title,
            prompt=chat.prompt,
            messages=messages,
        )

    @staticmethod
    def db_message_to_message_info(message: Message) -> MessageInfoResponse:
        return MessageInfoResponse(
            id=message.id,
            role=message.role,
            content=message.content,
        )
