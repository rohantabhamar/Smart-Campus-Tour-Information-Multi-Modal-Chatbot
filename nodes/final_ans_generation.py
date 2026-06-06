import time
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, SYSTEM_PROMPT, GROQ_MAX_RETRIES
from config.logger import get_logger

logger = get_logger(__name__)


_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model=GROQ_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            api_key=GROQ_API_KEY,
        )
    return _llm


def final_ans_generation(state: dict):
    logger.debug("final_ans_generation → entry")
    t0 = time.perf_counter()

    if state.get("error"):
        logger.warning(f"final_ans_generation → skipped: {state['error']}")
        return {"answer": f"Sorry, something went wrong: {state['error']}"}

    query = state.get("merge_query") or state.get("query", "")
    kb_context = state.get("kb_context", "")
    user_content = f"KB Context:\n{kb_context}\n\nUser Question:\n{query}"
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_content)]

    for attempt in range(1, GROQ_MAX_RETRIES + 1):
        try:
            response = get_llm().invoke(messages)
            answer = response.content.strip()
            logger.info(f"final_ans_generation → attempt={attempt} duration={time.perf_counter()-t0:.3f}s")
            return {"answer": answer}
        except Exception as e:
            logger.warning(f"final_ans_generation → attempt {attempt} failed: {e}")
            if attempt == GROQ_MAX_RETRIES:
                logger.error(f"final_ans_generation → all {GROQ_MAX_RETRIES} attempts failed", exc_info=True)
                return {"answer": "Sorry, I was unable to generate a response. Please try again."}
