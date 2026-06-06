import time
from services.kb_search import smart_search, format_kb_context, search_single, location_summary
from services.intent_extractor import extract_category_hints
from config.logger import get_logger

logger = get_logger(__name__)


def kb_search(state: dict):
    logger.debug("kb_search → entry")
    t0 = time.perf_counter()
    try:
        extracted = {
            "intent": state["intent"],
            "entities": state["entities"],
            "category_hints": state["category_hints"],
            "nav_pair": state["nav_pair"],
            "raw_query": state.get("merge_query") or state["query"],
        }

        # ── Navigation: search source and destination separately ──
        if state["intent"] == "navigation" and state.get("nav_pair"):
            nav = state["nav_pair"]
            src_text = nav["source"]
            dst_text = nav["destination"]

            src_r = search_single(src_text, extract_category_hints(src_text))
            dst_r = search_single(dst_text, extract_category_hints(dst_text))

            src_block = location_summary(src_r[0]) if src_r else f"'{src_text}' not found in KB"
            dst_block = location_summary(dst_r[0]) if dst_r else f"'{dst_text}' not found in KB"

            kb_context = f"Starting location:\n  {src_block}\n\nDestination:\n  {dst_block}"
            kb_results = (src_r or []) + (dst_r or [])
            is_list_mode = False

        # ── Regular / list query ──
        else:
            kb_results, is_list_mode = smart_search(extracted)
            kb_context = format_kb_context(kb_results, state["intent"], is_list_mode)

        logger.info(
            f"kb_search → results={len(kb_results)} "
            f"is_list_mode={is_list_mode} "
            f"duration={time.perf_counter()-t0:.3f}s"
        )

        return {
            "kb_results": kb_results,
            "kb_context": kb_context,
            "is_list_mode": is_list_mode,
        }
    except Exception as e:
        logger.error(f"kb_search → failed: {e}", exc_info=True)
        return {"error": str(e)}
