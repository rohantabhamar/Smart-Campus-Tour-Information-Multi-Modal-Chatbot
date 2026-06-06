import asyncio
import tempfile
import os
from fastapi import APIRouter, UploadFile, File
from api.schemas import ChatResponse
from core.audio_graph import audio_workflow
from config.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/query/audio", response_model=ChatResponse)
async def audio_query(file: UploadFile = File(...)):
    logger.info(f"audio endpoint → filename='{file.filename}'")
    # save uploaded file to a temp file then transcribe
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: audio_workflow.invoke({"query": tmp_path})
        )
    finally:
        os.unlink(tmp_path)
    return ChatResponse(
        answer   = result.get("answer", ""),
        pipeline = "audio",
        error    = result.get("error"),
    )