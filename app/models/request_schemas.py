from enum import StrEnum

from pydantic import BaseModel, Field


class OrderBy(StrEnum):
    ASC = "asc"
    DESC = "desc"


class ChatSortBy(StrEnum):
    ID = "id"
    DATETIME = "datetime"


class GetChatsInfoParams(BaseModel):
    sort_by: ChatSortBy = Field(default=ChatSortBy.DATETIME)
    order_by: OrderBy = Field(default=OrderBy.DESC)


class UserSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)


class CreateChatRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)


class UpdateChatRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)


class CreateMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    system_prompt: str | None = Field(None, min_length=1, max_length=300)
