import time
import numpy as np
from core.model_loader import get_faiss
from config.logger import get_logger

logger                      = get_logger(__name__)



def faiss_node(state: dict) :
    logger.debug("faiss_node → entry")
    t0    = time.perf_counter()
    try:
        faiss_index, image_records = get_faiss()
        query = np.array(state["embedding"], dtype="float32").reshape(1, -1)
        scores, indices = faiss_index.search(query, 3)

        top_3 = []
        for score, idx in zip(scores[0], indices[0]):
            record = image_records[idx]
            top_3.append({
                "score":    round(float(score), 3),
                "category": record["category"],
                "kb_name":  record["kb_name"],
            })


        non_self  = [r for r in top_3 if r["score"] < 0.999]
        best      = non_self[0] if non_self else top_3[0]
        logger.info(
            f"faiss_node → best_match={best['kb_name']} "
            f"score={best['score']} "
            f"duration={time.perf_counter()-t0:.3f}s"
        )

        return {
            "top_3_matches": top_3,
            "best_match":    best,
        }
    
    except Exception as e:
        logger.error(f"faiss_node → failed: {e}", exc_info=True)
        return {"error": str(e), "top_3_matches": [], "best_match": None}