from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from agents.orchestrator import run_copilot_query

router = APIRouter(prefix="/chat", tags=["chat"])


def extract_token(authorization: str | None) -> str:
    if authorization and authorization.startswith("Bearer "):
        return authorization[len("Bearer "):]
    return ""


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
async def chat(request: ChatRequest, authorization: str | None = Header(default=None)) -> ChatResponse:
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")

    try:
        result = await run_copilot_query(request.query, auth_token=extract_token(authorization))
    except Exception as exc:
        # The pipeline's own error handling is a future task (Ollama failures,
        # Data Service unreachable, etc). For now, surface a generic 500 rather
        # than leaking an internal stack trace to the client - this matches
        # the "never a raw crash during a live demo" principle from the guide,
        # even before the more detailed per-failure-mode handling exists.
        raise HTTPException(status_code=500, detail="Failed to generate a response") from exc

    return ChatResponse(answer=result["answer"], citations=result["citations"])
