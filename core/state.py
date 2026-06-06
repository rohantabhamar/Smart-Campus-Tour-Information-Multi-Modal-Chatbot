from typing import TypedDict


class AudioBotState(TypedDict):

    # ── Input ──────────────────────────────────────────────
    query: str | None

    # ── After extract_node ─────────────────────────────────
    intent: str
    entities: list[dict]
    category_hints: list[str]
    nav_pair: dict | None

    # ── After search_node ──────────────────────────────────
    kb_results: list[dict]
    kb_context: str
    is_list_mode: bool

    # ── After llm_node ─────────────────────────────────────
    answer: str
    error: str | None


class FAISSMatch(TypedDict):
    score: float
    category: str
    kb_name: str


class ImageBotState(TypedDict):

    # ── Input ─────────────────────────────────────
    image_path: str | None

    # ── After CLIP ────────────────────────────────
    embedding: list | None

    # ── After FAISS ───────────────────────────────
    top_3_matches: list[FAISSMatch] | None
    best_match: FAISSMatch | None

    # ── After KB lookup ───────────────────────────
    kb_info: str | None
    name: str | None
    description: str | None
    map_ref: str | None
    directions: str | None
    hours: dict | None
    events: list | None

    # ── After LLM ─────────────────────────────────
    answer: str | None
    error: str | None


class TextBotState(TypedDict):
    # ── Input ──────────────────────────────────────
    query: str

    # ── After extract_node ───────────────────────
    intent: str
    entities: list[dict]
    category_hints: list[str]
    nav_pair: dict | None

    # ── After search_node ─────────────────────────
    kb_results: list[dict]
    kb_context: str
    is_list_mode: bool

    # ── After llm_node ────────────────────────────
    answer: str
    error: str | None


class AudioTextBotState(TypedDict):
    # ── Input ──────────────────────────────────────────────
    text_query: str | None
    query: str

    # ── Murge query ────────────────────────────────────────
    merge_query: str
    # ── After extract_node ─────────────────────────────────
    intent: str
    entities: list[dict]
    category_hints: list[str]
    nav_pair: dict | None

    # ── After search_node ──────────────────────────────────
    kb_results: list[dict]
    kb_context: str
    is_list_mode: bool

    # ── After llm_node ─────────────────────────────────────
    answer: str
    error: str | None


class MultiModalState(TypedDict):
    # ── Inputs ────────────────────────────────────
    query: str | None
    audio_path: str | None
    image_path: str | None

    # ── After Whisper ─────────────────────────────
    transcript: str | None

    # ── After DistilBERT (text) ───────────────────
    text_intent: str | None
    text_intent_embedding: list | None

    # ── After DistilBERT (voice) ──────────────────
    voice_intent: str | None
    voice_intent_embedding: list | None

    # ── After CLIP + FAISS ────────────────────────
    image_embedding: list | None
    top_3_matches: list | None
    best_match: dict | None

    # ── After Fusion MLP ──────────────────────────
    fusion_location: str | None
    fusion_confidence: float | None

    # ── After KB search ───────────────────────────
    kb_context: str | None

    # ── LLM inputs (all three passed together) ────
    final_text_query: str | None
    final_voice_query: str | None
    final_image_location: str | None

    # ── After LLM ─────────────────────────────────
    answer: str | None
    error: str | None
