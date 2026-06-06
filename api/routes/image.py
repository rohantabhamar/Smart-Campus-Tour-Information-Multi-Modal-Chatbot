import asyncio
import tempfile
import os
from fastapi import APIRouter, UploadFile, File
from api.schemas import ChatResponse
from core.image_graph import image_workflow
from config.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/query/image", response_model=ChatResponse)
async def image_query(file: UploadFile = File(...)):
    logger.info(f"image endpoint → filename='{file.filename}'")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: image_workflow.invoke({"image_path": tmp_path})
        )
    finally:
        os.unlink(tmp_path)
    return ChatResponse(
        answer   = result.get("answer", ""),
        pipeline = "image",
        error    = result.get("error"),
    )