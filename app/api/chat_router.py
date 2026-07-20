from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Request, Response
from fastapi.responses import StreamingResponse

from app.dependencies import get_auth_service, get_chat_service
from app.models import (
    ChatHistoryResponse,
    ChatShortInfoResponse,
    CommonResponse,
    CreateChatRequest,
    CreateMessageRequest,
    GetChatsInfoParams,
    MessageInfoResponse,
    UpdateChatRequest,
)
from app.services import AuthService, ChatService

chat_router = APIRouter(prefix="/chats", tags=["Chats"])


@chat_router.post(path="", response_model=CommonResponse)
async def create_chat(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    data: Annotated[CreateChatRequest | None, Body()] = None,
) -> CommonResponse:
    user_id = await auth_service.get_current_user_id(request=request, response=response)
    return await chat_service.create_chat(
        user_id=user_id,
        title= data.title if data else None,
    )


@chat_router.put(path="/{chat_id}", response_model=CommonResponse)
async def update_chat(
    request: Request,
    response: Response,
    chat_id: Annotated[int, Path()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    data: Annotated[UpdateChatRequest, Body()],
) -> CommonResponse:
    user_id = await auth_service.get_current_user_id(request=request, response=response)
    return await chat_service.update_chat(
        user_id=user_id,
        chat_id=chat_id,
        data=data,
    )


@chat_router.get(path="", response_model=list[ChatShortInfoResponse])
async def get_chats(
    request: Request,
    response: Response,
    params: Annotated[GetChatsInfoParams, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> list[ChatShortInfoResponse]:
    user_id = await auth_service.get_current_user_id(request=request, response=response)
    return await chat_service.get_user_chats(user_id=user_id, params=params)


@chat_router.get(path="/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    request: Request,
    response: Response,
    chat_id: Annotated[int, Path()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatHistoryResponse:
    user_id = await auth_service.get_current_user_id(request=request, response=response)
    return await chat_service.get_chat_with_history(user_id=user_id, chat_id=chat_id)


@chat_router.delete(path="/{chat_id}", response_model=CommonResponse)
async def delete_chat(
    request: Request,
    response: Response,
    chat_id: Annotated[int, Path()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> CommonResponse:
    user_id = await auth_service.get_current_user_id(request=request, response=response)
    return await chat_service.delete_chat(
        user_id=user_id,
        chat_id=chat_id,
    )


@chat_router.post(path="/{chat_id}", response_model=MessageInfoResponse)
async def create_message(
    request: Request,
    response: Response,
    chat_id: Annotated[int, Path()],
    data: Annotated[CreateMessageRequest, Body()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    
) -> MessageInfoResponse:
    user_id = await auth_service.get_current_user_id(request=request, response=response)
    return await chat_service.send_message(
        chat_id=chat_id,
        user_id=user_id,
        data=data,
    )


@chat_router.post(path="/{chat_id}/stream")
async def create_message_stream(
    request: Request,
    response: Response,
    chat_id: Annotated[int, Path()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    data: Annotated[CreateMessageRequest, Body()],
) -> StreamingResponse:
    user_id = await auth_service.get_current_user_id(request=request, response=response)
    send_stream = await chat_service.send_message_stream(user_id=user_id, chat_id=chat_id, data=data)
    return StreamingResponse(send_stream, media_type="text/event-stream")
