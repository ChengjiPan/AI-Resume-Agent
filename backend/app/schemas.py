from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)


class SourceItem(BaseModel):
    file: str
    section: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


class IndexResponse(BaseModel):
    documents_indexed: int
    chunks_indexed: int
