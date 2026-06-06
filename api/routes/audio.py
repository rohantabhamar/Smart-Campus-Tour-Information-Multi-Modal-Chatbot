import asyncio
from fastapi import APIRouter
from api.schemas import AudioRequest, ChatResponse
from core.audio_graph import audio_workflow
from config.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/query/audio", response_model=ChatResponse)
async def audio_query(request: AudioRequest):
    from api.main import whisper_semaphore
    async with whisper_semaphore:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: audio_workflow.invoke({"query": request.audio_path})
        )
    return ChatResponse(answer=result.get("answer", ""), pipeline="audio", error=result.get("error"))
