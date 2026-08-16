from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.schemas import ChatRequest, ChatResponse, SourceItem
from app.services.rag import answer_question


app = FastAPI(title="AI Resume Assistant API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

WEB_PAGE = Path(__file__).resolve().parent / "static" / "index.html"


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    """Serve the recruiter-facing chat page from the same origin as the API."""
    return FileResponse(WEB_PAGE)


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True, "api_key_configured": settings.has_api_key}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not settings.has_api_key:
        raise HTTPException(500, "OPENAI_API_KEY is not configured.")
    try:
        answer, sources = answer_question(request.question, settings)
        return ChatResponse(answer=answer, sources=[SourceItem(**source) for source in sources])
    except RuntimeError as error:
        raise HTTPException(409, str(error)) from error
    except Exception as error:
        raise HTTPException(500, str(error)) from error

