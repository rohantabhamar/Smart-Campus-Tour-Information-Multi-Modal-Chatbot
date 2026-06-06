import asyncio
from fastapi import APIRouter
from api.schemas import ImageRequest, ChatResponse
from core.image_graph import image_workflow
from config.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/query/image", response_model=ChatResponse)
async def image_query(request: ImageRequest):
    from api.main import clip_semaphore
    async with clip_semaphore:
        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: image_workflow.invoke({"image_path": request.image_path})
        )
    return ChatResponse(answer=result.get("answer",""), pipeline="image", error=result.get("error"))