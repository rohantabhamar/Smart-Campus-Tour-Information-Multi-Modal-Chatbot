from pydantic import BaseModel, Field
from typing import Optional


# ── Requests ──────────────────────────────────────────────────────────────

class TextRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class AudioTextRequest(BaseModel):
    text_query: Optional[str] = Field(None, description="Optional text query")


class MultiModalRequest(BaseModel):
    query: Optional[str] = Field(None, description="Text query")


# ── Response ──────────────────────────────────────────────────────────────

class ChatResponse(BaseModel):
    answer: str
    pipeline: str
    error: Optional[str] = None
