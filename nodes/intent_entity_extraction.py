import time
from models.rules_model.rules_extractor import extract_rules
from config.logger import get_logger

logger = get_logger(__name__)


def intent_entity_extraction(state: dict):
    logger.debug("intent_entity_extraction → entry")
    t0 = time.perf_counter()
    try:
        query  = state["query"]
        result = extract_rules(query)
        entities = [
            {"text": e, "type": "misc", "score": 1.0}
            for e in result["entities"]
        ]
        logger.info(
            f"intent_entity_extraction → intent={result['intent']} "
            f"entities={result['entities']} "
            f"category_hints={result['category_hints']} "
            f"duration={time.perf_counter()-t0:.3f}s"
        )
        return {
            "intent":         result["intent"],
            "entities":       entities,
            "category_hints": result["category_hints"],
            "nav_pair":       result["nav_pair"],
        }
    except Exception as e:
        logger.error(f"intent_entity_extraction → failed: {e}", exc_info=True)
        return {"error": str(e)}
