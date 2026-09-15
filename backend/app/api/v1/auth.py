from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.db.postgres.models import User
from app.schemas import UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user
