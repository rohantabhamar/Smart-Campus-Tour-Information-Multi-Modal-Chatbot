import time
from config.logger import get_logger
logger = get_logger(__name__)

def text_input (state:dict):
    logger.debug("text_input node → entry")
    t0         = time.perf_counter()
    try:
        query = state["text_query"]
        logger.info(f"text_input node → duration={time.perf_counter()-t0:.3f}s")
        return {"text_query":query}
    
    except Exception as e:
        logger.error(f"text input → failed: {e}", exc_info=True)
        return {"error": str(e)}