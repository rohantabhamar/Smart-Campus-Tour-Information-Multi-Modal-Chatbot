import asyncio
import tempfile
import os
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from api.schemas import ChatResponse
from core.multimodel_graph import multimodal_workflow
from config.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/query/multimodal", response_model=ChatResponse)
async def multimodal_query(
    query: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    image_file: Optional[UploadFile] = File(None),
):
    logger.info(f"multimodal endpoint → text={query} audio={audio_file} image={image_file}")

    audio_path = None
    image_path = None

    try:
        if audio_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(await audio_file.read())
                audio_path = tmp.name

        if image_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(await image_file.read())
                image_path = tmp.name

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: multimodal_workflow.invoke({
                "query": query,
                "audio_path": audio_path,
                "image_path": image_path,
                "transcript": None, "text_intent": None,
                "text_intent_embedding": None, "voice_intent": None,
                "voice_intent_embedding": None, "image_embedding": None,
                "top_3_matches": None, "best_match": None,
                "fusion_location": None, "fusion_confidence": None,
                "kb_context": None, "final_text_query": None,
                "final_voice_query": None, "final_image_location": None,
                "answer": None, "error": None,
            })
        )
    finally:
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)

    return ChatResponse(
        answer=result.get("answer", ""),
        pipeline="multimodal",
        error=result.get("error"),
    )
