import asyncio
from fastapi import APIRouter
from api.schemas import AudioTextRequest, ChatResponse
from core.audio_with_text_graph import audio_text_workflow
from config.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/query/audio-text", response_model=ChatResponse)
async def audio_text_query(request: AudioTextRequest):
    from api.main import whisper_semaphore
    async with whisper_semaphore:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: audio_text_workflow.invoke({
                "query": request.query,
                "text_query": request.text_query,
            })
        )
    return ChatResponse(answer=result.get("answer", ""), pipeline="audio-text", error=result.get("error"))
