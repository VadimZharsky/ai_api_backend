from datetime import datetime

from pydantic import BaseModel, Field


class CommonResponse(BaseModel):
    status: bool = Field(default=True)
    message: str


class UserDataResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    created_at: datetime


class ChatShortInfoResponse(BaseModel):
    id: int
    title: str


class MessageInfoResponse(BaseModel):
    id: int
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    id: int
    title: str
    prompt: str
    messages: list[MessageInfoResponse]
