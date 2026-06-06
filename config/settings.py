from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
from config.secrets import load_secrets

# ── Load correct .env file based on APP_ENV ──────────────────────────────
APP_ENV = os.getenv("APP_ENV", "dev")
env_file = Path(__file__).resolve().parent.parent / f".env.{APP_ENV}"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()   # fallback to .env

# ── Load secrets ─────────────────────────────────────────────────────────
_secrets = load_secrets()

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
KB_PATH = DATA_DIR / "campus_kb.json"
FAQ_PATH = DATA_DIR / "text" / "faq.csv"
IMAGE_PATH = DATA_DIR / "image" / "images"
AUDIO_PATH = DATA_DIR / "audio_samples"
MODELS_DIR = BASE_DIR / "models"
DISTILBERT_DIR = MODELS_DIR / "distilbert_campus"
FAISS_DIR = MODELS_DIR / "clip_faiss"
FUSION_MLP_DIR = MODELS_DIR / "fusion_mlp"
SPACY_DIR = MODELS_DIR / "campus_spacy" / "output" / "model-best"
RULES_DIR = MODELS_DIR / "rules_model"

# ── API Keys (now from secrets manager) ──────────────────────────────────
GROQ_API_KEY = _secrets.get("GROQ_API_KEY", "")
HF_API_TOKEN = _secrets.get("HUGGINGFACE_API_TOKEN", "")

# ── LLM settings ─────────────────────────────────────────────────────────
GROQ_MODEL = "llama-3.1-8b-instant"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 512
GROQ_MAX_RETRIES = 3

# ── Memory settings ───────────────────────────────────────────────────────
MEMORY_WINDOW_SIZE = 5

# ── KB search settings ────────────────────────────────────────────────────
KB_TOP_N = 3
KB_SCORE_THRESHOLD = 10.0
KB_NAV_THRESHOLD = 5.0

# ── System prompt ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a helpful campus navigation assistant for a university. "
    "Answer ONLY using the KB context provided. Never make up information. "
    "Use exact values from the KB context. "
    "ALWAYS respond in this exact structured format — no exceptions:\n\n"
    "LOCATION: <name of the location or N/A>\n"
    "FLOOR: <floor and block reference or N/A>\n"
    "DIRECTIONS: <step by step directions or N/A>\n"
    "HOURS: <opening hours or N/A>\n"
    "EVENTS: <upcoming events or N/A>\n"
    "ANSWER: <a friendly 1-3 sentence summary answer to the user question>\n\n"
    "Rules:\n"
    "- Every field must be present even if the value is N/A.\n"
    "- For FROM-TO navigation, DIRECTIONS must mention starting floor AND destination floor.\n"
    "- For list queries, ANSWER must state the exact count and list all entries.\n"
    "- For image queries, LOCATION must be the identified place name.\n"
    "- Keep ANSWER concise, friendly, and helpful.\n"
    "- Never add any text outside this format.\n"
    "- Never refer to locations not in the KB context."
)


def validate() -> None:
    """Call at startup. Raises RuntimeError if any critical config is missing."""
    issues = []

    if not GROQ_API_KEY:
        issues.append("GROQ_API_KEY is not set")
    if not HF_API_TOKEN:
        issues.append("HUGGINGFACE_API_TOKEN is not set")
    if not KB_PATH.exists():
        issues.append(f"KB file not found: {KB_PATH}")
    if not DISTILBERT_DIR.exists():
        issues.append(f"DistilBERT model not found: {DISTILBERT_DIR}")
    if not FAISS_DIR.exists():
        issues.append(f"FAISS index not found: {FAISS_DIR}")
    if not FUSION_MLP_DIR.exists():
        issues.append(f"Fusion MLP not found: {FUSION_MLP_DIR}")

    if issues:
        raise RuntimeError(
            f"[{APP_ENV}] Startup config validation failed:\n" +
            "\n".join(f"  - {i}" for i in issues)
        )


# ── Model versions ────────────────────────────────────────────────────────
MODEL_VERSIONS = {
    "whisper": "base",
    "clip": "ViT-B/32",
    "distilbert": "distilbert-base-uncased",
    "fusion_mlp": "v1",
    "faiss": "v1",
    "spacy": "en_core_web_md-3.8.0",
}
