import asyncio
from fastapi import APIRouter
from api.schemas import MultiModalRequest, ChatResponse
from core.multimodel_graph import multimodal_workflow
from config.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/query/multimodal", response_model=ChatResponse)
async def multimodal_query(request: MultiModalRequest):
    from api.main import whisper_semaphore, clip_semaphore
    async with whisper_semaphore, clip_semaphore:
        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: multimodal_workflow.invoke({
                "query":      request.query,
                "audio_path": request.audio_path,
                "image_path": request.image_path,
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
    return ChatResponse(answer=result.get("answer",""), pipeline="multimodal", error=result.get("error"))