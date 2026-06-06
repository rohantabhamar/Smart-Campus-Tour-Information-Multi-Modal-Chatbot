# Rule base intent and entity classifier
import re
import json

INTENT_PATTERNS = {
    "find_location": [
        r"\bwhere\b", r"\blocation\b", r"\bdirections?\b",
        r"\bhow (do i|to) (get|reach|find|go)\b",
        r"\bfind\b", r"\bnavigate\b", r"\broom\b", r"\bfloor\b", r"\bbuilding\b",
    ],
    "opening_hours": [
        r"\bopen(ing)?\b", r"\bclos(e|ing|ed)\b", r"\bhours?\b",
        r"\btime\b", r"\bwhen\b", r"\bschedule\b", r"\btiming\b",
        r"\bopen on\b",
    ],
    "events": [
        r"\bevents?\b", r"\bworkshops?\b", r"\bseminars?\b",
        r"\bfestival\b", r"\bupcoming\b", r"\bhappening\b",
        r"\bcompetitions?\b", r"\bhackathon\b", r"\bfairs?\b",
        r"\bactivit(y|ies)\b", r"\bon at\b", r"\banything on\b",
        r"\bscheduled\b", r"\bexhibition\b", r"\bexpo\b",
        r"\bare there any\b",
    ],
    "description": [
        r"\bwhat is\b", r"\btell me about\b", r"\bdescribe\b",
        r"\bfacilities?\b", r"\bservices?\b", r"\bdetails?\b",
    ],
    "navigation": [
        r"\bfrom\b.+\bto\b", r"\bgo from\b", r"\broute from\b",
    ],
}

CATEGORY_KEYWORDS = {
    "library":        ["library", "books", "reading"],
    "cafeteria":      ["cafeteria", "canteen", "food", "eat", "meal"],
    "gym":            ["gym", "fitness", "sports", "yoga", "workout"],
    "it_lab":         ["it lab", "computer lab", "pc"],
    "department":     ["department", "dept"],
    "hod_office":     ["hod", "head of department"],
    "auditorium":     ["auditorium"],
    "medical_center": ["medical", "health", "clinic", "doctor"],
    "career_center":  ["career", "job", "placement"],
    "student_union":  ["student union", "union", "lounge"],
    "admin_office":   ["admission", "registry", "enrollment"],
    "lab":            ["lab", "laboratory"],
    "classroom":      ["classroom"],
    "seminar_room":   ["seminar room", "seminar"],
    "printing_room":  ["print", "photocopy"],
    "security_office":["security", "guard"],
}

ENTITY_MAP = {
    "library":         ["library", "books", "study desks", "place to study", "reading"],
    "cafeteria":       ["cafeteria", "canteen", "food", "eat", "meal", "dining area", "hungry"],
    "coffee shop":     ["coffee", "cafe", "hot drink", "coffee shop"],
    "student union":   ["student union", "su", "socialise", "social area", "student lounge"],
    "gym":             ["gym", "fitness", "sports centre", "exercise", "run", "workout", "sports"],
    "it lab":          ["it lab", "computer lab", "pc", "use a computer", "computer room"],
    "printing":        ["print", "printing room", "photocopy"],
    "admissions":      ["admissions", "registry", "student id", "registration", "enrollment", "dissertation"],
    "career":          ["career centre", "career services", "career advice", "cv help",
                        "cv workshop", "job listings", "careers and employability",
                        "career fair", "career events", "employability"],
    "medical":         ["medical", "doctor", "health centre", "unwell", "clinic", "health"],
    "auditorium":      ["auditorium", "main hall", "graduation"],
    "security":        ["security", "lost item", "campus security", "guard"],
    "research lab":    ["research lab", "innovation centre", "hackathon", "innovation", "research events"],
    "garden":          ["garden", "outdoor", "outside", "benches"],
    "accommodation":   ["accommodation", "housing", "student housing"],
    "engineering":     ["engineering block", "engineering college", "engineering building",
                        "engineering entrance", "engineering fest", "project exhibition",
                        "industry interaction", "final year project"],
    "department":      ["department", "dept"],
    "hod office":      ["hod", "head of department"],
    "seminar room":    ["seminar room", "seminar"],
    "classroom":       ["classroom"],
    "lecture hall":    ["lecture hall", "lecture theatre", "lecture hall a", "main lecture"],
}

OFFICIAL_ENTITY_NAME = {
    "library":       "Main Library",
    "cafeteria":     "Main Cafeteria",
    "coffee shop":   "Campus Coffee Shop",
    "student union": "Student Union",
    "gym":           "Sports & Fitness Centre",
    "it lab":        "IT & Computer Lab",
    "printing":      "Printing & Stationery Centre",
    "admissions":    "Admissions & Registry Office",
    "career":        "Career Services Centre",
    "medical":       "Medical & Counselling Centre",
    "auditorium":    "Main Auditorium",
    "security":      "Campus Security Office",
    "research lab":  "Research & Innovation Lab",
    "garden":        "Campus Garden & Outdoor Study Area",
    "accommodation": "Student Accommodation Office",
    "engineering":   "Engineering College - Main Block",
    "department":    "department",
    "hod office":    "hod_office",
    "seminar room":  "Seminar Room Block",
    "classroom":     "classroom",
}
from config.settings import KB_PATH
with open(KB_PATH, encoding="utf-8") as f:
    _KB = json.load(f)

KB_ENTITY_MAP = {}
for entry in _KB:
    name = entry["name"]
    KB_ENTITY_MAP[name.lower()] = name
    if entry.get("room_number"):
        KB_ENTITY_MAP[entry["room_number"].lower()] = name

DEPT_TO_HOD = {
    "mechanical": "HOD Office ME-HOD101",
    "chemical":   "HOD Office CE-HOD202",
    "information technology": "HOD Office IT-HOD303",
    "computer":   "HOD Office CSE-HOD404",
    "cse":        "HOD Office CSE-HOD404",
    "entc":       "HOD Office ENTC-HOD505",
    "electrical": "HOD Office EE-HOD606",
    "civil":      "HOD Office CVL-HOD707",
}

DEPT_TO_TR = {
    "mechanical": "Teachers Room ME-TR101",
    "chemical":   "Teachers Room CE-TR202",
    "information technology": "Teachers Room IT-TR303",
    "computer":   "Teachers Room CSE-TR404",
    "cse":        "Teachers Room CSE-TR404",
    "entc":       "Teachers Room ENTC-TR505",
    "electrical": "Teachers Room EE-TR606",
    "civil":      "Teachers Room CVL-TR707",
}

DEPT_TO_NAME = {
    "mechanical engineering": "Mechanical Engineering Department",
    "chemical engineering":   "Chemical Engineering Department",
    "information technology": "Information Technology Department",
    "computer engineering":   "Computer Engineering Department",
    "entc":                   "Electronics & Telecommunication (ENTC) Department",
    "electrical engineering": "Electrical Engineering Department",
    "civil engineering":      "Civil Engineering Department",
}

NAV_SPLIT     = re.compile(r"\bfrom\s+(.+?)\s+to\s+(.+?)(?:\?|$)", re.IGNORECASE)
NAV_STOPWORDS = {"the","a","an","how","do","i","go","get","way","route","travel"}


def rules_classify_intent(query):
    q = query.lower()
    scores = {intent: 0 for intent in INTENT_PATTERNS}
    for intent, patterns in INTENT_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, q):
                scores[intent] += 1
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "general"


def rules_category_hints(query):
    q = query.lower()
    return [cat for cat, kws in CATEGORY_KEYWORDS.items() if any(kw in q for kw in kws)]


def rules_nav_pair(query):
    m = NAV_SPLIT.search(query)
    if m:
        src = " ".join(w for w in m.group(1).split() if w.lower() not in NAV_STOPWORDS)
        dst = " ".join(w for w in m.group(2).split() if w.lower() not in NAV_STOPWORDS)
        if src and dst:
            return {"source": src, "destination": dst}
    return None


def rules_extract_entities(query):
    q = query.lower()
    found = []
    if any(kw in q for kw in ["teachers room", "faculty room", "staff room", "professor in"]):
        for dept_key, tr_name in DEPT_TO_TR.items():
            if dept_key in q:
                return [tr_name]
    if any(kw in q for kw in ["hod", "head of", "hod office", "hod room"]):
        for dept_key, hod_name in DEPT_TO_HOD.items():
            if dept_key in q:
                return [hod_name]
    for name_lower, official_name in KB_ENTITY_MAP.items():
        if name_lower in q:
            if official_name not in found:
                found.append(official_name)
    if found:
        return found
    for dept_kw, dept_name in DEPT_TO_NAME.items():
        if dept_kw in q:
            if dept_name not in found:
                found.append(dept_name)
    if found:
        return found
    for key, keywords in ENTITY_MAP.items():
        if any(kw in q for kw in keywords):
            official = OFFICIAL_ENTITY_NAME.get(key, key)
            if official not in found:
                found.append(official)
    return found


def extract_rules(query):
    intent   = rules_classify_intent(query)
    nav_pair = rules_nav_pair(query) if intent == "navigation" else None
    return {
        "intent":         intent,
        "entities":       rules_extract_entities(query),
        "category_hints": rules_category_hints(query),
        "nav_pair":       nav_pair,
        "raw_query":      query,
        "source":         "rules",
    }


def extract_with_fallback(query):
    return extract_rules(query)
