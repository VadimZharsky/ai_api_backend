from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class TokenPayload(BaseModel):
    iat: datetime
    nbf: datetime
    exp: datetime
    sub: str


class MessageRoleType(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class LlmMessage:
    role: MessageRoleType
    content: str
