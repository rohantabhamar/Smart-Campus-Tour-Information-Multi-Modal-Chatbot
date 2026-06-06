import time
import torch
from PIL import Image
from core.model_loader import get_clip_model
from config.logger import get_logger

logger              = get_logger(__name__)
device              = "cuda" if torch.cuda.is_available() else "cpu"





def clip_node(state: dict):
    logger.debug("clip_node → entry")
    t0         = time.perf_counter()
    try:
        clip_model, clip_preprocess = get_clip_model()
        image_path = state["image_path"]
        image =clip_preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(device)
        
        with torch.no_grad():
            embedding =clip_model.encode_image(image)
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        logger.info(f"clip_node → image={image_path} duration={time.perf_counter()-t0:.3f}s")
        return {"embedding": embedding.cpu().numpy().squeeze().tolist()}
    
    except FileNotFoundError:
        logger.error(f"clip_node → image file not found: {state.get('image_path')}")
        return {"error": "Image file not found."}
    except Exception as e:
        logger.error(f"clip_node → failed: {e}", exc_info=True)
        return {"error": str(e)}
     