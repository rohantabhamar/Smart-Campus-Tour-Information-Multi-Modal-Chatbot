import asyncio
from fastapi import APIRouter
from api.schemas import TextRequest, ChatResponse
from core.text_graph import text_workflow
from config.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/query/text", response_model=ChatResponse)
async def text_query(request: TextRequest):
    logger.info(f"text endpoint → query='{request.query}'")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: text_workflow.invoke({"query": request.query})
    )
    return ChatResponse(
        answer=result.get("answer", ""),
        pipeline="text",
        error=result.get("error"),
    )
