import time
from config.logger import get_logger
logger = get_logger(__name__)

def merge_query(state: dict):
    logger.debug("merge node → entry")
    t0         = time.perf_counter()
    try:
        text_query = state["text_query"]
        query            = state["query"]

        if query and text_query:
            merged = f"{query} {text_query}".strip()
        elif query:
            merged = query
        else:
            merged = text_query
        
        logger.info(f"merge node → duration={time.perf_counter()-t0:.3f}s")

        return {"merge_query": merged}
    except Exception as e:
        logger.error(f"merge_query → failed: {e}", exc_info=True)
        return {"error": str(e)}