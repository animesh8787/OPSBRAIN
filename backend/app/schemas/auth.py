from datetime import datetime
from uuid import UUID

from app.schemas.common import ORMBase


class UserResponse(ORMBase):
    id: UUID
    # Plain str, not EmailStr: a user's email either comes straight from
    # Firebase (which already validated it at signup) or, for a token with no
    # email at all, from get_current_user's synthesized fallback - which
    # EmailStr rejects outright, since email-validator treats .local as a
    # reserved TLD regardless of syntax. No need to re-validate either case.
    email: str
    role: str
    created_at: datetime
