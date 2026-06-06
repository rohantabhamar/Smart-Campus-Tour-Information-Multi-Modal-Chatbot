import asyncio
import tempfile
import os
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from api.schemas import ChatResponse
from core.audio_with_text_graph import audio_text_workflow
from config.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/query/audio-text", response_model=ChatResponse)
async def audio_text_query(
    file: UploadFile = File(...),
    text_query: Optional[str] = Form(None)
):
    logger.info(f"audio-text endpoint → filename='{file.filename}' text='{text_query}'")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: audio_text_workflow.invoke({
                "query":      tmp_path,
                "text_query": text_query,
            })
        )
    finally:
        os.unlink(tmp_path)
    return ChatResponse(
        answer   = result.get("answer", ""),
        pipeline = "audio-text",
        error    = result.get("error"),
    )