from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from agents.orchestrator import run_copilot_query
from app.core.dependencies import get_current_user
from app.db.postgres.models import User

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str


class CitationOut(BaseModel):
    index: int
    chunk_id: str
    document_id: str
    document_filename: str
    page_number: int | None
    content: str
    score: float
    citation_verified: bool


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationOut]


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user)) -> ChatResponse:
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")

    try:
        result = await run_copilot_query(request.query)
    except Exception as exc:
        # The pipeline's own error handling is a future task (Ollama failures,
        # Data Service unreachable, etc). For now, surface a generic 500 rather
        # than leaking an internal stack trace to the client - this matches
        # the "never a raw crash during a live demo" principle from the guide,
        # even before the more detailed per-failure-mode handling exists.
        raise HTTPException(status_code=500, detail="Failed to generate a response") from exc

    return ChatResponse(answer=result["answer"], citations=result["citations"])
