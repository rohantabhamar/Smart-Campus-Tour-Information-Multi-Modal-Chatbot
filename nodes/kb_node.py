import time
from core.model_loader import get_kb
from config.logger import get_logger

logger = get_logger(__name__)


def kb_node(state: dict):
    logger.debug("kb_node → entry")
    t0 = time.perf_counter()

    try:
        kb_lookup = get_kb()

        best_match = state["best_match"]
        kb_name = best_match["kb_name"]

        entry = kb_lookup.get(kb_name, {})

        logger.info(f"kb_node → kb_name={kb_name} found={bool(entry)} duration={time.perf_counter()-t0:.3f}s")

        return {
            "kb_info": kb_name,
            "name": entry.get("name", "N/A"),
            "description": entry.get("description", "N/A"),
            "map_ref": entry.get("map_reference", "N/A"),
            "directions": entry.get("directions_from_entrance", "N/A"),
            "hours": entry.get("opening_hours", {}),
            "events": entry.get("events", []),
        }

    except Exception as e:
        logger.error(f"kb_node → failed: {e}", exc_info=True)
        return {"error": str(e)}
