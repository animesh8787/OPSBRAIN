from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.common import ORMBase


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: UUID  # user id
    exp: int
    type: str  # values: "access" or "refresh"


class UserResponse(ORMBase):
    id: UUID
    email: EmailStr
    role: str
    created_at: datetime
