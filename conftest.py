import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# ── Mock KB data ──────────────────────────────────────────────────────────
MOCK_KB_ENTRY = {
    "name":                      "Library",
    "description":               "Main campus library",
    "map_reference":             "Block A, Floor 2",
    "directions_from_entrance":  "Enter main gate, turn left, go up stairs",
    "opening_hours":             {"Mon-Fri": "8am-8pm", "Sat": "9am-5pm"},
    "events":                    ["Book fair on June 10"],
    "category":                  "academic",
}

MOCK_KB_LOOKUP = {"Library": MOCK_KB_ENTRY}

@pytest.fixture
def mock_kb(monkeypatch):
    monkeypatch.setattr("core.model_loader.get_kb", lambda: MOCK_KB_LOOKUP)
    monkeypatch.setattr("nodes.kb_node.get_kb", lambda: MOCK_KB_LOOKUP)  # ← add this
    return MOCK_KB_LOOKUP

@pytest.fixture
def mock_llm(monkeypatch):
    mock = MagicMock()
    mock.invoke.return_value.content = "The library is on Floor 2 of Block A."
    monkeypatch.setattr("nodes.final_ans_generation.llm", mock)
    monkeypatch.setattr("nodes.llm_node.llm", mock)
    return mock

@pytest.fixture
def mock_whisper(monkeypatch):
    mock = MagicMock()
    mock.transcribe.return_value = {"text": "where is the library"}
    monkeypatch.setattr("core.model_loader.get_whisper_model", lambda: mock)
    monkeypatch.setattr("nodes.audio_to_text.get_whisper_model", lambda: mock)
    return mock

@pytest.fixture
def mock_clip(monkeypatch):
    import torch
    mock_model      = MagicMock()
    mock_preprocess = MagicMock()
    dummy_emb       = torch.ones(1, 512)
    mock_model.encode_image.return_value = dummy_emb
    mock_preprocess.return_value         = torch.zeros(3, 224, 224)
    monkeypatch.setattr("nodes.clip_node.clip_model",      mock_model)
    monkeypatch.setattr("nodes.clip_node.clip_preprocess", mock_preprocess)
    return mock_model, mock_preprocess

@pytest.fixture
def mock_faiss(monkeypatch):
    import numpy as np
    mock_index   = MagicMock()
    mock_records = [
        {"category": "academic", "kb_name": "Library"},
        {"category": "academic", "kb_name": "Library"},
        {"category": "academic", "kb_name": "Library"},
    ]
    mock_index.search.return_value = (
        np.array([[0.95, 0.80, 0.60]]),
        np.array([[0, 1, 2]])
    )
    monkeypatch.setattr("nodes.faiss_node.get_faiss", lambda: (mock_index, mock_records))
    return mock_index, mock_records

@pytest.fixture
def base_text_state():
    return {
        "query":          "Where is the library?",
        "intent":         "location",
        "entities":       [{"text": "library", "type": "misc", "score": 1.0}],
        "category_hints": ["academic"],
        "nav_pair":       None,
        "kb_results":     [MOCK_KB_ENTRY],
        "kb_context":     "Name: Library\nDescription: Main campus library",
        "is_list_mode":   False,
        "answer":         None,
        "error":          None,
    }

@pytest.fixture
def base_image_state():
    return {
        "image_path":    "data/images/library/library_01.jpg",
        "embedding":     [0.1] * 512,
        "top_3_matches": None,
        "best_match":    {"score": 0.95, "category": "academic", "kb_name": "Library"},
        "kb_info":       "Library",
        "name":          "Library",
        "description":   "Main campus library",
        "map_ref":       "Block A, Floor 2",
        "directions":    "Turn left at entrance",
        "hours":         {"Mon-Fri": "8am-8pm"},
        "events":        [],
        "answer":        None,
        "error":         None,
    }