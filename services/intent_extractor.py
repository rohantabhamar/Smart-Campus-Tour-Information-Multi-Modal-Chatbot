"""
services/intent_extractor.py
-----------------------------
Pure business logic for intent classification and entity extraction.
No graph awareness — can be used and tested independently.

Intent classes:
  find_location  – user wants directions / where something is
  opening_hours  – user wants to know when something opens/closes
  events         – user wants to know about upcoming events
  description    – user wants a general description of a place
  navigation     – user wants to go FROM one place TO another
  general        – fallback
"""

from __future__ import annotations
import re

# ---------------------------------------------------------------------------
# Intent keyword patterns
# ---------------------------------------------------------------------------
_INTENT_PATTERNS: dict[str, list[str]] = {
    "find_location": [
        r"\bwhere\b", r"\blocation\b", r"\bdirections?\b",
        r"\bhow (do i|to) (get|reach|find|go)\b",
        r"\bfind\b", r"\bnavigate\b", r"\bmap\b", r"\broom\b",
        r"\bfloor\b", r"\bbuilding\b",
        r"\bwhich (block|building|floor|room)\b",
    ],
    "opening_hours": [
        r"\bopen(ing)?\b", r"\bclos(e|ing|ed)\b", r"\bhours?\b",
        r"\btime\b", r"\bwhen\b", r"\bschedule\b",
        r"\bavailable\b", r"\btiming\b",
    ],
    "events": [
        r"\bevents?\b", r"\bworkshop\b", r"\bseminar\b", r"\blecture\b",
        r"\bfestival\b", r"\bcompetition\b", r"\bfair\b", r"\btoday\b",
        r"\bthis week\b", r"\bupcoming\b", r"\bhappening\b",
    ],
    "description": [
        r"\bwhat is\b", r"\btell me about\b", r"\bdescribe\b",
        r"\binfo(rmation)?\b", r"\bdetails?\b", r"\bfeatures?\b",
        r"\bfacilities?\b", r"\bservices?\b",
    ],
    "navigation": [
        r"\bfrom\b.+\bto\b",
        r"\bgo from\b",
        r"\bhow (do i|to) go from\b",
        r"\bway from\b",
        r"\broute from\b",
        r"\bget from\b",
        r"\btravel from\b",
        r"\bmove from\b",
    ],
}

# ---------------------------------------------------------------------------
# Category keyword mapping
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "library":             ["library", "books", "reading", "journal", "study"],
    "cafeteria":           ["cafeteria", "canteen", "food", "eat", "meal", "lunch", "dinner", "breakfast", "dining"],
    "gym":                 ["gym", "fitness", "sports", "yoga", "workout", "exercise", "basketball"],
    "it_lab":              ["it lab", "computer lab", "pc", "workstation", "programming lab"],
    "lecture_hall":        ["lecture hall", "auditorium", "hall", "lecture"],
    "student_union":       ["student union", "union", "lounge", "games room"],
    "admin_office":        ["admission", "registry", "enrollment", "transcript", "id card"],
    "career_center":       ["career", "job", "internship", "cv", "placement"],
    "medical_center":      ["medical", "health", "clinic", "doctor", "nurse", "pharmacy"],
    "department":          ["department", "dept"],
    "hod_office":          ["hod", "head of department"],
    "seminar_room":        ["seminar room", "seminar"],
    "classroom":           ["classroom", "class room"],
    "lab":                 ["lab", "laboratory"],
    "printing_room":       ["print", "photocopy", "xerox"],
    "security_office":     ["security", "guard"],
    "outdoor":             ["garden", "parking", "park", "outdoor"],
    "teachers_room":       ["teacher", "faculty", "staff room"],
    "engineering_college": ["engineering block", "engineering college", "engg"],
    "auditorium":          ["auditorium"],
}

# ---------------------------------------------------------------------------
# Navigation split
# ---------------------------------------------------------------------------
_NAV_SPLIT  = re.compile(r"\bfrom\s+(.+?)\s+to\s+(.+?)(?:\?|$)", re.IGNORECASE)
_NAV_STOPS  = {"the","a","an","please","how","do","i","go","get",
               "way","route","travel","move","can","you","tell","me"}


def _clean_nav(text: str) -> str:
    return " ".join(w for w in text.strip().split() if w.lower() not in _NAV_STOPS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_intent(query: str) -> str:
    q = query.lower()
    scores = {intent: 0 for intent in _INTENT_PATTERNS}
    for intent, patterns in _INTENT_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, q):
                scores[intent] += 1
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "general"


def extract_entities(query: str) -> list[dict]:
    """Capitalised phrase extraction — lightweight, no model needed."""
    words = re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", query)
    return [{"text": w, "type": "misc", "score": 1.0} for w in words]


def extract_category_hints(query: str) -> list[str]:
    q = query.lower()
    return [cat for cat, kws in CATEGORY_KEYWORDS.items() if any(kw in q for kw in kws)]


def extract_navigation_pair(query: str) -> dict | None:
    m = _NAV_SPLIT.search(query)
    if m:
        src = _clean_nav(m.group(1))
        dst = _clean_nav(m.group(2))
        if src and dst:
            return {"source": src, "destination": dst}
    return None


def extract(query: str) -> dict:
    """
    Full extraction — returns intent, entities, category_hints, nav_pair.
    This is the main function called by extract_node.
    """
    intent   = classify_intent(query)
    nav_pair = extract_navigation_pair(query) if intent == "navigation" else None
    return {
        "intent":         intent,
        "entities":       extract_entities(query),
        "category_hints": extract_category_hints(query),
        "nav_pair":       nav_pair,
        "raw_query":      query,
    }
