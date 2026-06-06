import time
from core.model_loader import get_whisper_model
from config.logger import get_logger

logger = get_logger(__name__)


def audio_to_text(state: dict):
    logger.debug("audio_to_text → entry")
    t0 = time.perf_counter()
    try:
        whisper_model = get_whisper_model()
        audio_query = state['query']
        query = whisper_model.transcribe(audio_query)
        logger.info(
            f"audio_to_text → transcript='{query['text'][:80]}...' "
            f"duration={time.perf_counter()-t0:.3f}s"
        )
        return {'query': query['text']}
    except FileNotFoundError:
        logger.error(f"audio_to_text → audio file not found: {state.get('query')}")
        return {"error": "Audio file not found."}
    except Exception as e:
        logger.error(f"audio_to_text → failed: {e}", exc_info=True)
        return {"error": str(e)}
