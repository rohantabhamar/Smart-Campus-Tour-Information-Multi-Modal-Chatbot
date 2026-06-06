"""
core/model_loader.py
"""
import torch
import json
import torch.nn as nn


DEVICE = torch.device("cpu")


class FusionMLP(nn.Module):
    def __init__(self, input_dim=1280, num_classes=11):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 512), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(512, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.network(x)


_whisper_model = None
_clip_model = None
_clip_preprocess = None
_db_tokenizer = None
_db_base_model = None
_faiss_index = None
_image_records = None
_kb_lookup = None
_fusion = None


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            _whisper_model = whisper.load_model("base")
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}") from e
    return _whisper_model


def get_clip_model():
    global _clip_model, _clip_preprocess
    if _clip_model is None:
        try:
            import clip
            _clip_model, _clip_preprocess = clip.load("ViT-B/32", device=DEVICE)
            _clip_model.eval()
        except Exception as e:
            raise RuntimeError(f"Failed to load clip model: {e}") from e
    return _clip_model, _clip_preprocess


def get_distilbert():
    global _db_tokenizer, _db_base_model
    if _db_tokenizer is None:
        try:
            from transformers import DistilBertTokenizer, DistilBertModel
            from config.settings import DISTILBERT_DIR
            _db_tokenizer = DistilBertTokenizer.from_pretrained(str(DISTILBERT_DIR))
            _db_base_model = DistilBertModel.from_pretrained("distilbert-base-uncased").to(DEVICE)
            _db_base_model.eval()
        except Exception as e:
            raise RuntimeError(f"Failed to load distilbert model:{e}") from e
    return _db_tokenizer, _db_base_model


def get_faiss():
    global _faiss_index, _image_records
    if _faiss_index is None:
        try:
            import faiss
            import pickle
            from config.settings import FAISS_DIR
            _faiss_index = faiss.read_index(str(FAISS_DIR / "campus_index.faiss"))
            with open(FAISS_DIR / "image_records.pkl", "rb") as f:
                _image_records = pickle.load(f)

        except Exception as e:
            raise RuntimeError(f"Failed to load faiss model: {e}") from e
    return _faiss_index, _image_records


def get_kb():
    global _kb_lookup
    if _kb_lookup is None:
        try:
            from config.settings import KB_PATH
            with open(KB_PATH, encoding="utf-8") as f:
                kb = json.load(f)
            _kb_lookup = {entry["name"]: entry for entry in kb}

        except Exception as e:
            raise RuntimeError(f"Failed to load KB: {e}") from e
    return _kb_lookup


def get_fusion_mlp():
    global _fusion
    if _fusion is None:
        try:
            from config.settings import FUSION_MLP_DIR
            checkpoint = torch.load(
                FUSION_MLP_DIR / "fusion_mlp.pt",
                map_location=DEVICE,
                weights_only=False,
            )
            model = FusionMLP(
                input_dim=1280,
                num_classes=len(checkpoint["idx_to_class"]),
            ).to(DEVICE)
            model.load_state_dict(checkpoint["model_state_dict"])
            model.eval()
            _fusion = (model, checkpoint["idx_to_class"])
        except Exception as e:
            raise RuntimeError(f"Failed to load fusion model: {e}") from e
    return _fusion


def health_check() -> dict:
    """
    Verifies all models and files are accessible.
    Called at startup by api/main.py.
    Returns dict of status per model.
    """
    from config.settings import (
        KB_PATH, FAISS_DIR, DISTILBERT_DIR,
        FUSION_MLP_DIR, SPACY_DIR
    )
    results = {}

    results["kb"] = "ok" if KB_PATH.exists() else "missing"
    results["faiss_index"] = "ok" if (FAISS_DIR / "campus_index.faiss").exists() else "missing"
    results["faiss_records"] = "ok" if (FAISS_DIR / "image_records.pkl").exists() else "missing"
    results["distilbert"] = "ok" if DISTILBERT_DIR.exists() else "missing"
    results["fusion_mlp"] = "ok" if (FUSION_MLP_DIR / "fusion_mlp.pt").exists() else "missing"
    results["spacy"] = "ok" if SPACY_DIR.exists() else "missing"

    failed = [k for k, v in results.items() if v != "ok"]
    results["status"] = "healthy" if not failed else f"unhealthy: {failed}"
    return results
