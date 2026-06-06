import time
from langchain_groq import ChatGroq
from config.settings import GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, GROQ_MAX_RETRIES
from config.logger import get_logger

logger = get_logger(__name__)

llm = ChatGroq(
    model       = GROQ_MODEL,
    temperature = LLM_TEMPERATURE,
    max_tokens  = LLM_MAX_TOKENS,
    api_key     = GROQ_API_KEY,
)

def llm_node(state: dict):
    logger.debug("llm_node → entry")
    t0 = time.perf_counter()

    if state.get("error"):
        logger.warning(f"llm_node → skipped due to upstream error: {state['error']}")
        return {"answer": f"Sorry, something went wrong: {state['error']}"}

    prompt = f"""
    You are a campus navigation assistant.

    The user uploaded an image. It was identified as: {state['name']} 
    (confidence: {state['best_match']['score'] if state.get('best_match') else 'N/A'})
    Location   : {state['map_ref']}
    Directions : {state['directions']}
    Hours      : {state['hours']}
    Events     : {state['events']}
    Description: {state['description']}

    First briefly tell the user what location was found and its key details.
    Then ask: "Would you like directions, opening hours, or event information?"
    Keep it friendly and concise.
    """

    for attempt in range(1, GROQ_MAX_RETRIES + 1):
        try:
            response = llm.invoke(prompt)
            logger.info(f"llm_node → attempt={attempt} duration={time.perf_counter()-t0:.3f}s")
            return {"answer": response.content.strip()}
        except Exception as e:
            logger.warning(f"llm_node → attempt {attempt} failed: {e}")
            if attempt == GROQ_MAX_RETRIES:
                logger.error(f"llm_node → all {GROQ_MAX_RETRIES} attempts failed", exc_info=True)
                return {"answer": "Sorry, I was unable to generate a response. Please try again."}