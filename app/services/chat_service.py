from collections.abc import AsyncGenerator

from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.llm import ILlmClient
from app.db import Chat, ChatRepository, Message, MessageRepository, db_context
from app.exceptions import EntityNotFoundError
from app.models import (
    ChatHistoryResponse,
    ChatShortInfoResponse,
    CommonResponse,
    CreateMessageRequest,
    GetChatsInfoParams,
    MessageInfoResponse,
    MessageRoleType,
    UpdateChatRequest,
)
from app.tools.loggers import ILogger
from app.tools.mappers import ChatMapper, LlmMapper


class ChatService:
    def __init__(
        self,
        session: AsyncSession,
        logger: ILogger,
        llm_client: ILlmClient
    ) -> None:
        self._session: AsyncSession = session
        self._logger: ILogger = logger
        self._llm_client: ILlmClient = llm_client

    async def create_chat(self, user_id: int, title: str | None) -> CommonResponse:
        chat = Chat(
            user_id=user_id,
            title=title if title else "new chat",
            prompt="",
        )
        await ChatRepository.create(
            session=self._session,
            entity=chat,
            logger=self._logger,
        )
        resp = CommonResponse(
            message=f"chat with id {chat.id} created",
        )
        await self._session.commit()
        return resp

    async def update_chat(self, user_id: int, chat_id: int, data: UpdateChatRequest) -> CommonResponse:
        chat = await self._get_chat_or_404(user_id=user_id, chat_id=chat_id)
        if data.title is not None:
            chat.title = data.title
        await ChatRepository.update(
            session=self._session,
            entity=chat,
            logger=self._logger,
        )
        resp = CommonResponse(
            message=f"chat with id {chat.id} updated",
        )
        await self._session.commit()
        return resp

    async def send_message(
        self,
        chat_id: int,
        user_id: int,
        data: CreateMessageRequest,
        context_limit: int = 15,
    ) -> MessageInfoResponse:
        chat = await self._get_chat_or_404(user_id=user_id, chat_id=chat_id)
        message = Message(
            chat_id=chat.id,
            role=MessageRoleType.USER,
            content=data.message,
        )
        await MessageRepository.create(
            session=self._session,
            entity=message,
            logger=self._logger,
        )
        history = await MessageRepository.get_with_limit(
            session=self._session,
            chat_id=chat_id,
            limit=context_limit,
            logger=self._logger,
        )
        system_prompt = ChatService._resolve_system_prompt(
            old=chat.prompt,
            new=data.system_prompt,
        )
        message_payload = LlmMapper.build_messages_for_llm(
            history=history,
            system_prompt=system_prompt,
        )
        ai_response = await self._llm_client.send_chat_completion(
            messages=message_payload,
        )
        assistant_msg = Message(
            chat_id=chat_id,
            role=MessageRoleType.ASSISTANT,
            content=ai_response
        )
        await MessageRepository.create(
            session=self._session,
            entity=assistant_msg,
            logger=self._logger,
        )
        if system_prompt != chat.prompt:
            await ChatRepository.refresh_chat_updated_at_time_with_prompt(
                session=self._session,
                chat_id=chat_id,
                prompt=system_prompt,
                logger=self._logger,
            )
        else:
            await ChatRepository.refresh_chat_updated_at_time(
                session=self._session,
                chat_id=chat_id,
                logger=self._logger,
            )
        resp = MessageInfoResponse(
            id=assistant_msg.id,
            role=assistant_msg.role,
            content=assistant_msg.content,
        )
        await self._session.commit()
        return resp

    async def send_message_stream(
        self,
        user_id: int,
        chat_id: int,
        data: CreateMessageRequest,
        context_limit: int = 15,
    ) -> AsyncGenerator[str]:
        chat = await self._get_chat_or_404(user_id=user_id, chat_id=chat_id)
        chat_prompt = chat.prompt

        message = Message(
            chat_id=chat.id,
            role=MessageRoleType.USER,
            content=data.message,
        )
        await MessageRepository.create(
            session=self._session,
            entity=message,
            logger=self._logger,
        )
        await self._session.commit()

        history = await MessageRepository.get_with_limit(
            session=self._session,
            chat_id=chat_id,
            limit=context_limit,
            logger=self._logger,
        )
        system_prompt = ChatService._resolve_system_prompt(
            old=chat_prompt,
            new=data.system_prompt,
        )
        message_payload = LlmMapper.build_messages_for_llm(
            history=history,
            system_prompt=system_prompt,
        )
        llm_stream = self._llm_client.send_chat_completion_stream(messages=message_payload)

        async def stream_generator() -> AsyncGenerator[str]:
            response_chunks: list[str] = []
            async for token in llm_stream:
                if token:
                    response_chunks.append(token)
                    yield f"data: {token}\n\n"

            full_response_text = "".join(response_chunks)
            async with db_context.session() as private_session:
                assistant_message = Message(
                    chat_id=chat_id,
                    role=MessageRoleType.ASSISTANT,
                    content=full_response_text,
                )
                await MessageRepository.create(
                    session=private_session,
                    entity=assistant_message,
                    logger=self._logger,
                )
                if system_prompt != chat_prompt:
                    await ChatRepository.refresh_chat_updated_at_time_with_prompt(
                        session=private_session,
                        chat_id=chat_id,
                        prompt=system_prompt,
                        logger=self._logger,
                    )
                else:
                    await ChatRepository.refresh_chat_updated_at_time(
                        session=private_session,
                        chat_id=chat_id,
                        logger=self._logger,
                    )
                await private_session.commit()

        return stream_generator()

    async def delete_chat(self, user_id: int, chat_id: int) -> CommonResponse:
        chat = await self._get_chat_or_404(user_id=user_id, chat_id=chat_id)
        await ChatRepository.delete(
            session=self._session,
            entity=chat,
            logger=self._logger,
        )
        await self._session.commit()
        return CommonResponse(message=f"chat with chat_id {chat_id} deleted")

    async def get_chat_with_history(self, user_id: int, chat_id: int) -> ChatHistoryResponse:
        chat = await ChatRepository.get_chat_with_history(
            session=self._session,
            user_id=user_id,
            chat_id=chat_id,
            logger=self._logger,
        )
        if chat is None:
            raise EntityNotFoundError(f"chat with chat_id {chat_id} and user_id {user_id} not found")
        return ChatMapper.db_chat_to_chat_history_info(chat=chat)

    async def get_user_chats(self, user_id: int, params: GetChatsInfoParams) -> list[ChatShortInfoResponse]:
        rows = await ChatRepository.get_chats_info_by_user_id(
            session=self._session,
            user_id=user_id,
            params=params,
            logger=self._logger
        )
        if len(rows) == 0:
            return []
        ta = TypeAdapter(list[ChatShortInfoResponse])
        return ta.validate_python(rows)

    async def _get_chat_or_404(self, user_id: int, chat_id: int) -> Chat:
        chat = await ChatRepository.get(
            session=self._session,
            user_id=user_id,
            chat_id=chat_id,
            logger=self._logger,
        )
        if chat is None:
            raise EntityNotFoundError(f"chat with chat_id {chat_id} and user_id {user_id} not found")
        return chat

    @staticmethod
    def _resolve_system_prompt(old: str, new: str | None) -> str:
        if new is None:
            return old
        if new is not None and new != "" and new != old:
            return new
        return old
