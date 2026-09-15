from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.common import ORMBase


class UserResponse(ORMBase):
    id: UUID
    email: EmailStr
    role: str
    created_at: datetime
