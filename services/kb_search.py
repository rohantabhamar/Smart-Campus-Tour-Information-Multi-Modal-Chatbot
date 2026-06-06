"""
services/kb_search.py
---------------------
Pure KB search logic — no graph awareness.
Loads campus_kb.json and provides scored search, category search,
and context formatting.
"""

from __future__ import annotations
import json
import re
from pathlib import Path
from rapidfuzz import fuzz
from config.settings import KB_PATH, KB_TOP_N, KB_SCORE_THRESHOLD, KB_NAV_THRESHOLD

# ---------------------------------------------------------------------------
# Load and index KB
# ---------------------------------------------------------------------------

def _load_kb(path: Path = KB_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for entry in data:
        entry["_search_text"] = " ".join(filter(None, [
            entry.get("name", ""),
            entry.get("description", ""),
            entry.get("category", ""),
            entry.get("map_reference", ""),
            entry.get("department", ""),
            entry.get("room_number", ""),
            entry.get("nearby_landmarks", ""),
        ])).lower()
    return data


_KB: list[dict] = _load_kb()

# ---------------------------------------------------------------------------
# List query detection
# ---------------------------------------------------------------------------
_LIST_PATTERNS = [
    r"\bhow many\b", r"\ball\b", r"\blist\b",
    r"\bcount\b",    r"\btotal\b", r"\bevery\b", r"\bshow all\b",
]

def is_list_query(query: str) -> bool:
    q = query.lower()
    return any(re.search(pat, q) for pat in _LIST_PATTERNS)

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score_entry(entry: dict, query_lower: str,
                 entity_texts: list[str], category_hints: list[str]) -> float:
    score      = 0.0
    name_lower = entry.get("name", "").lower()
    st         = entry["_search_text"]

    if query_lower in name_lower or name_lower in query_lower:
        score += 80
    for ent in entity_texts:
        if ent.lower() in name_lower:   score += 60
        elif ent.lower() in st:         score += 20
    if entry.get("category") in category_hints:
        score += 40
    score += fuzz.token_set_ratio(query_lower, name_lower) * 0.3
    for word in re.findall(r"\w+", query_lower):
        if len(word) > 3 and word in st:
            score += 5

    return score

# ---------------------------------------------------------------------------
# Public search API
# ---------------------------------------------------------------------------

def search_by_category(category_hints: list[str]) -> list[dict]:
    """Return ALL KB entries matching any of the given categories."""
    return [e for e in _KB if e.get("category") in category_hints]


def search(extracted: dict,
           top_n: int = KB_TOP_N,
           score_threshold: float = KB_SCORE_THRESHOLD) -> list[dict]:
    """Scored search — returns top_n best matching KB entries."""
    query_lower    = extracted["raw_query"].lower()
    entity_texts   = [e["text"] for e in extracted.get("entities", [])]
    category_hints = extracted.get("category_hints", [])

    scored = []
    for entry in _KB:
        s = _score_entry(entry, query_lower, entity_texts, category_hints)
        if s >= score_threshold:
            scored.append({**entry, "_score": round(s, 2)})

    scored.sort(key=lambda x: x["_score"], reverse=True)
    return scored[:top_n]


def search_single(query_text: str, category_hints: list[str],
                  top_n: int = 1,
                  score_threshold: float = KB_NAV_THRESHOLD) -> list[dict]:
    """
    Search for a single location text (used in navigation node).
    Lower default threshold since location names are short.
    """
    extracted = {
        "raw_query":      query_text,
        "entities":       [],
        "category_hints": category_hints,
    }
    return search(extracted, top_n=top_n, score_threshold=score_threshold)


def smart_search(extracted: dict,
                 default_top_n: int = KB_TOP_N) -> tuple[list[dict], bool]:
    """
    Auto-detect list/count queries and switch to category-wide search.
    Returns (results, is_list_mode).
    """
    query          = extracted["raw_query"]
    category_hints = extracted.get("category_hints", [])

    if is_list_query(query) and category_hints:
        return search_by_category(category_hints), True

    return search(extracted, top_n=default_top_n), False

# ---------------------------------------------------------------------------
# Context formatter
# ---------------------------------------------------------------------------

def format_kb_context(results: list[dict], intent: str,
                      is_list_mode: bool = False) -> str:
    if not results:
        return "No matching locations found in the campus knowledge base."

    lines = []

    if is_list_mode:
        lines.append(f"Total found: {len(results)}\n")
        for i, r in enumerate(results, 1):
            line = f"{i}. {r['name']}"
            if r.get("map_reference"): line += f" — {r['map_reference']}"
            if r.get("department"):    line += f" ({r['department']})"
            lines.append(line)
    else:
        for i, r in enumerate(results, 1):
            lines.append(f"[Result {i}] {r['name']} (category: {r['category']})")
            lines.append(f"  Map reference : {r.get('map_reference', 'N/A')}")
            lines.append(f"  Description   : {r.get('description', 'N/A')}")
            lines.append(f"  Directions    : {r.get('directions_from_entrance', 'N/A')}")

            hours = r.get("opening_hours", {})
            if hours:
                hours_str = ", ".join(f"{d}: {h}" for d, h in hours.items())
                lines.append(f"  Opening hours : {hours_str}")

            events = r.get("events", [])
            if events:
                lines.append(f"  Events        : {'; '.join(events)}")

            if r.get("nearby_landmarks"):
                lines.append(f"  Nearby        : {r['nearby_landmarks']}")

            if r.get("directions_by_floor"):
                floor_str = " | ".join(f"{k}: {v}" for k, v in r["directions_by_floor"].items())
                lines.append(f"  By floor      : {floor_str}")

            lines.append("")

    return "\n".join(lines)


def location_summary(entry: dict) -> str:
    """Compact summary of a KB entry for navigation prompts."""
    parts = [entry.get("name", "Unknown")]
    if entry.get("floor") is not None:
        parts.append(f"Floor: {entry['floor']}")
    if entry.get("map_reference"):
        parts.append(f"Location: {entry['map_reference']}")
    if entry.get("directions_from_entrance"):
        parts.append("Directions from entrance: " + entry["directions_from_entrance"])
    if entry.get("nearby_landmarks"):
        parts.append("Nearby: " + entry["nearby_landmarks"])
    return "\n  ".join(parts)
