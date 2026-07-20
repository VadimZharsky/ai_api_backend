from collections.abc import AsyncIterator
from typing import override

from openai import APIError, AsyncOpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from app.clients.llm.i_llm_client import ILlmClient
from app.exceptions import LlmError
from app.models import LlmMessage, MessageRoleType
from app.tools.loggers import ILogger
from app_config import app_settings


class OpenaiClient(ILlmClient):
    def __init__(self, logger: ILogger) -> None:
        self._logger: ILogger = logger
        self._model: str = app_settings.llm_model.lower()
        self._is_reasoning: bool = "pro" in self._model or "r1" in self._model
        base_url = app_settings.llm_base_url

        if app_settings.llm_provider == "ollama" and not base_url.endswith("/v1"):
            base_url = f"{base_url.rstrip('/')}/v1"

        self._client: AsyncOpenAI = AsyncOpenAI(
            api_key=app_settings.llm_api_key or "ollama-dummy-key",
            base_url=base_url,
            timeout=60.0,
        )

    @override
    async def close(self) -> None:
        await self._client.close()

    @override
    async def send_chat_completion_stream(self, messages: list[LlmMessage]) -> AsyncIterator[str]:
        llm_messages = OpenaiClient._cast_messages(messages)
        try:
            if self._is_reasoning:
                response = await self._client.chat.completions.create(
                    model=app_settings.llm_model,
                    messages=llm_messages,
                    stream=True,
                    reasoning_effort="high",
                    extra_body={"thinking": {"type": "enabled"}},
                )
            else:
                response = await self._client.chat.completions.create(
                    model=app_settings.llm_model,
                    messages=llm_messages,
                    stream=True,
                    temperature=0.7
                )
            async for chunk in response:
                token = chunk.choices[0].delta.content or ""
                if token:
                    yield token

        except APIError as exc:
            self._logger.error(f"LLM Provider API Error: {exc.message})")
            raise LlmError(f"LLM Service error: {exc.message}") from exc

        except Exception as exc:
            self._logger.error(f"Unexpected error in LlmProxyClient: {exc}")
            raise LlmError("Failed to communicate with LLM provider") from exc

    @override
    async def send_chat_completion(self, messages: list[LlmMessage]) -> str:
        llm_messages = OpenaiClient._cast_messages(messages)
        try:
            if self._is_reasoning:
                response = await self._client.chat.completions.create(
                    model=app_settings.llm_model,
                    messages=llm_messages,
                    stream=False,
                    reasoning_effort="high",
                    extra_body={"thinking": {"type": "enabled"}},
                )
            else:
                response = await self._client.chat.completions.create(
                    model=app_settings.llm_model,
                    messages=llm_messages,
                    stream=False,
                    temperature=0.7
                )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Received empty response from LLM provider")

            return content

        except APIError as exc:
            self._logger.error(f"LLM Provider API Error: {exc.message})")
            raise LlmError(f"LLM Service error: {exc.message}") from exc

        except Exception as exc:
            self._logger.error(f"Unexpected error in LlmProxyClient: {exc}")
            raise LlmError("Failed to communicate with LLM provider") from exc

    @staticmethod
    def _cast_messages(messages: list[LlmMessage]) -> list[ChatCompletionMessageParam]:
        llm_messages: list[ChatCompletionMessageParam] = []
        for message in messages:
            match message.role:
                case MessageRoleType.SYSTEM:
                    system_msg: ChatCompletionSystemMessageParam = {"role": "system", "content": message.content}
                    llm_messages.append(system_msg)
                case MessageRoleType.USER:
                    user_msg: ChatCompletionUserMessageParam = {"role": "user", "content": message.content}
                    llm_messages.append(user_msg)
                case MessageRoleType.ASSISTANT:
                    assistant_msg: ChatCompletionAssistantMessageParam = {
                        "role": "assistant", "content": message.content
                    }
                    llm_messages.append(assistant_msg)
                    
        return llm_messages
