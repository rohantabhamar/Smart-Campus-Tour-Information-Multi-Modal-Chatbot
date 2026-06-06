from pydantic import BaseModel, Field
from typing import Optional


# ── Requests ──────────────────────────────────────────────────────────────

class TextRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class AudioRequest(BaseModel):
    audio_path: str = Field(..., description="Absolute path to audio file on server")


class ImageRequest(BaseModel):
    image_path: str = Field(..., description="Absolute path to image file on server")


class AudioTextRequest(BaseModel):
    query: str = Field(..., description="Audio file path")
    text_query: Optional[str] = Field(None, description="Optional text query")


class MultiModalRequest(BaseModel):
    query: Optional[str] = Field(None, description="Text query")
    audio_path: Optional[str] = Field(None, description="Audio file path")
    image_path: Optional[str] = Field(None, description="Image file path")


# ── Response ──────────────────────────────────────────────────────────────

class ChatResponse(BaseModel):
    answer: str
    pipeline: str
    error: Optional[str] = None
