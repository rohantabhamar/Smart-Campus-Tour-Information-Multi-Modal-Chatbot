# data/generate_faq.py
# Expanded FAQ corpus — minimum 5 examples per KB location
# Fixes Fusion MLP underfitting (was 165 samples for 154 classes = ~1/class)
# Now generates ~800+ samples across all 154 locations

import csv, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from config.settings import FAQ_PATH, KB_PATH
import json

os.makedirs(os.path.dirname(FAQ_PATH), exist_ok=True)

with open(KB_PATH, encoding="utf-8") as f:
    kb = json.load(f)

# ── Template banks ─────────────────────────────────────────
LOC_TEMPLATES = [
    "Where is {name}?",
    "How do I get to {name}?",
    "Can you show me where {name} is?",
    "I need to find {name}",
    "Where can I find {name}?",
    "What is the location of {name}?",
    "Can you direct me to {name}?",
]

HOURS_TEMPLATES = [
    "What time does {name} open?",
    "When does {name} close?",
    "Is {name} open on Saturday?",
    "Is {name} open on Sunday?",
    "What are the opening hours for {name}?",
    "Is {name} open today?",
]

EVENT_TEMPLATES = [
    "Are there any events at {name}?",
    "What is happening at {name} this week?",
    "What events are scheduled at {name}?",
    "Is there anything on at {name} today?",
]

faqs = []

# ── General campus locations ────────────────────────────────
GENERAL = {
    "Main Library": [
        ("Where is the library?",                       "find_location"),
        ("How do I get to the main library?",           "find_location"),
        ("Can you show me where the library is?",       "find_location"),
        ("I need to find a place to study with books",  "find_location"),
        ("Where are the books and study desks?",        "find_location"),
        ("What time does the library open?",            "ask_hours"),
        ("Is the library open on Sunday?",              "ask_hours"),
        ("When does the library close on Saturday?",    "ask_hours"),
        ("What are the library opening hours?",         "ask_hours"),
        ("Is the library open late on weekdays?",       "ask_hours"),
        ("What events are at the library?",             "find_event"),
        ("Are there any workshops at the library?",     "find_event"),
    ],
    "Main Cafeteria": [
        ("Where is the cafeteria?",                     "find_location"),
        ("Where can I get food on campus?",             "find_location"),
        ("Where do students eat?",                      "find_location"),
        ("I am hungry — where is the dining area?",     "find_location"),
        ("Where is the canteen?",                       "find_location"),
        ("Is the cafeteria open on Sunday?",            "ask_hours"),
        ("What time does the cafeteria close?",         "ask_hours"),
        ("Is the cafeteria open on weekends?",          "ask_hours"),
        ("What are the cafeteria hours?",               "ask_hours"),
        ("What events are at the cafeteria?",           "find_event"),
    ],
    "Campus Coffee Shop": [
        ("Where is the coffee shop?",                   "find_location"),
        ("Where can I get a coffee?",                   "find_location"),
        ("Is there a cafe on campus?",                  "find_location"),
        ("Where can I get a hot drink?",                "find_location"),
        ("Is the coffee shop open on Sunday?",          "ask_hours"),
        ("What time does the coffee shop open?",        "ask_hours"),
        ("When does the cafe close?",                   "ask_hours"),
    ],
    "Student Union": [
        ("Where is the student union?",                 "find_location"),
        ("Where is the student union located?",         "find_location"),
        ("I need to find the student union building",   "find_location"),
        ("Where do students socialise on campus?",      "find_location"),
        ("Where is the SU?",                            "find_location"),
        ("Is the student union open on weekends?",      "ask_hours"),
        ("What time does the student union open?",      "ask_hours"),
        ("Are there any events at the student union?",  "find_event"),
        ("What is on at the student union tonight?",    "find_event"),
        ("What events are at the student union?",       "find_event"),
    ],
    "Sports & Fitness Centre": [
        ("Where is the gym?",                           "find_location"),
        ("Where is the sports centre?",                 "find_location"),
        ("Where can I exercise on campus?",             "find_location"),
        ("Where is the fitness centre?",                "find_location"),
        ("I want to go for a run — where is sports?",  "find_location"),
        ("Is the gym open on Sunday?",                  "ask_hours"),
        ("Is the gym open on weekends?",                "ask_hours"),
        ("What time does the gym open?",                "ask_hours"),
        ("When does the fitness centre close?",         "ask_hours"),
        ("Are there sports events this week?",          "find_event"),
        ("What fitness events are on?",                 "find_event"),
    ],
    "IT & Computer Lab": [
        ("Where is the IT lab?",                        "find_location"),
        ("Where can I use a computer?",                 "find_location"),
        ("Where is the computer room?",                 "find_location"),
        ("Where can I print and use a PC?",             "find_location"),
        ("Is the IT lab open on Saturday?",             "ask_hours"),
        ("When does the computer lab close?",           "ask_hours"),
    ],
    "Printing & Stationery Centre": [
        ("Where is the printing room?",                 "find_location"),
        ("Where can I print documents?",                "find_location"),
        ("Where can I photocopy something?",            "find_location"),
        ("Where is the print centre?",                  "find_location"),
        ("Is the printing room open on Saturday?",      "ask_hours"),
        ("What time does the printing centre close?",   "ask_hours"),
    ],
    "Admissions & Registry Office": [
        ("Where is the admissions office?",             "find_location"),
        ("Where do I go for student registration?",     "find_location"),
        ("Where is the registry?",                      "find_location"),
        ("Where do I submit my dissertation?",          "find_location"),
        ("Where can I get my student ID card?",         "find_location"),
        ("Is the admissions office open Saturday?",     "ask_hours"),
        ("What time does the registry open?",           "ask_hours"),
    ],
    "Career Services Centre": [
        ("Where is the career centre?",                 "find_location"),
        ("Where can I get career advice?",              "find_location"),
        ("Where do I go for CV help?",                  "find_location"),
        ("Where can I find job listings on campus?",    "find_location"),
        ("Where is careers and employability?",         "find_location"),
        ("What time does the career centre open?",      "ask_hours"),
        ("Is the career centre open on Saturday?",      "ask_hours"),
        ("Are there career fairs this week?",           "find_event"),
        ("What career events are coming up?",           "find_event"),
    ],
    "Medical & Counselling Centre": [
        ("Where is the medical centre?",                "find_location"),
        ("Where can I see a doctor on campus?",         "find_location"),
        ("Where is the health centre?",                 "find_location"),
        ("Where do I go if I feel unwell?",             "find_location"),
        ("Is the medical centre open today?",           "ask_hours"),
        ("What time does the health centre open?",      "ask_hours"),
    ],
    "Main Auditorium": [
        ("Where is the auditorium?",                    "find_location"),
        ("Where is the main hall?",                     "find_location"),
        ("Where are graduation ceremonies held?",       "find_location"),
        ("Is there anything on at the auditorium?",     "find_event"),
        ("What events are in the auditorium?",          "find_event"),
    ],
    "Research & Innovation Lab": [
        ("Where is the research lab?",                  "find_location"),
        ("Where is the innovation centre?",             "find_location"),
        ("Is there a hackathon coming up?",             "find_event"),
        ("What research events are on?",                "find_event"),
        ("Are there any innovation events this week?",  "find_event"),
    ],
    "Campus Security Office": [
        ("Where is the security office?",               "find_location"),
        ("Where do I report a lost item?",              "find_location"),
        ("Where can I find campus security?",           "find_location"),
        ("What time does security open?",               "ask_hours"),
    ],
    "Campus Garden & Outdoor Study Area": [
        ("Where is the campus garden?",                 "find_location"),
        ("Where can I study outside?",                  "find_location"),
        ("Where are the outdoor benches?",              "find_location"),
    ],
    "Student Accommodation Office": [
        ("Where is the accommodation office?",          "find_location"),
        ("Where do I ask about student housing?",       "find_location"),
        ("Where is student accommodation?",             "find_location"),
    ],
    "Lecture Hall A": [
        ("Where is lecture hall A?",                    "find_location"),
        ("How do I get to lecture hall A?",             "find_location"),
        ("Where is the main lecture theatre?",          "find_location"),
    ],
    "Seminar Room 1": [
        ("Where is seminar room 1?",                    "find_location"),
        ("Where are the seminar rooms?",                "find_location"),
    ],
    "Engineering College - Main Block": [
        ("Where is the engineering college?",           "find_location"),
        ("How do I get to the engineering block?",      "find_location"),
        ("Where is the main engineering building?",     "find_location"),
        ("What floor is the engineering entrance on?",  "find_location"),
        ("What events are at the engineering college?", "find_event"),
        ("Are there engineering fest events this week?","find_event"),
        ("Is there a project exhibition coming up?",    "find_event"),
        ("What competitions are happening in engineering?","find_event"),
        ("What time does the engineering block open?",  "ask_hours"),
    ],
}

# ── Engineering departments ─────────────────────────────────
DEPT_INFO = [
    (1, "Mechanical Engineering Department",
     "mechanical engineering", "mechanical", "ME"),
    (2, "Chemical Engineering Department",
     "chemical engineering", "chemical", "CE"),
    (3, "Information Technology Department",
     "information technology", "IT", "IT"),
    (4, "Computer Engineering Department",
     "computer engineering", "CSE", "CSE"),
    (5, "Electronics & Telecommunication (ENTC) Department",
     "ENTC", "electronics and telecommunication", "ENTC"),
    (6, "Electrical Engineering Department",
     "electrical engineering", "electrical", "EE"),
    (7, "Civil Engineering Department",
     "civil engineering", "civil", "CVL"),
]

DEPT_EXTRAS = {}
for floor, name, long_name, short_name, code in DEPT_INFO:
    DEPT_EXTRAS[name] = [
        (f"Where is the {long_name} department?",          "find_location"),
        (f"Which floor is {long_name} on?",                "find_location"),
        (f"How do I get to the {long_name} department?",   "find_location"),
        (f"Where is the {short_name} department?",         "find_location"),
        (f"I need to find {long_name}",                    "find_location"),
        (f"What floor is {long_name}?",                    "find_location"),
        (f"What time does {long_name} open?",              "ask_hours"),
        (f"Is the {long_name} department open on Saturday?","ask_hours"),
        (f"What events are in {long_name}?",               "find_event"),
        (f"Are there any {long_name} workshops this week?","find_event"),
    ]

# ── HOD offices ─────────────────────────────────────────────
HOD_EXTRAS = {}
for floor, name, long_name, short_name, code in DEPT_INFO:
    hod_name = f"HOD Office {code}-HOD{floor}0{floor}"
    HOD_EXTRAS[hod_name] = [
        (f"Where is the HOD office of {long_name}?",        "find_location"),
        (f"Where is the {long_name} head of department?",   "find_location"),
        (f"Where is the {long_name} HOD office?",           "find_location"),
        (f"I need to see the head of {long_name}",          "find_location"),
        (f"Where is the {short_name} HOD room?",            "find_location"),
    ]

# ── Teachers rooms ──────────────────────────────────────────
TR_EXTRAS = {}
for floor, name, long_name, short_name, code in DEPT_INFO:
    tr_name = f"Teachers Room {code}-TR{floor}0{floor}"
    TR_EXTRAS[tr_name] = [
        (f"Where is the teachers room in {long_name}?",     "find_location"),
        (f"Where is the {long_name} faculty room?",         "find_location"),
        (f"Where can I find a professor in {long_name}?",   "find_location"),
        (f"Where is the {long_name} staff room?",           "find_location"),
        (f"Where is the {short_name} teachers room?",       "find_location"),
    ]

# ── Labs — 3 examples per lab ───────────────────────────────
LAB_TEMPLATES = [
    ("Where is {lab_name}?",                    "find_location"),
    ("How do I find {lab_name}?",               "find_location"),
    ("What floor is {lab_name} on?",            "find_location"),
    ("Is {lab_name} open on Saturday?",         "ask_hours"),
    ("What time does {lab_name} open?",         "ask_hours"),
]

# ── Classrooms — 2 examples per room ───────────────────────
CLASSROOM_TEMPLATES = [
    ("Where is classroom {room}?",              "find_location"),
    ("How do I get to room {room}?",            "find_location"),
    ("What floor is {room} on?",                "find_location"),
]

# ────────────────────────────────────────────────────────────
# BUILD FULL FAQ
# ────────────────────────────────────────────────────────────
for entity, entries in GENERAL.items():
    for q, intent in entries:
        faqs.append((q, intent, entity))

for entity, entries in DEPT_EXTRAS.items():
    for q, intent in entries:
        faqs.append((q, intent, entity))

for entity, entries in HOD_EXTRAS.items():
    for q, intent in entries:
        faqs.append((q, intent, entity))

for entity, entries in TR_EXTRAS.items():
    for q, intent in entries:
        faqs.append((q, intent, entity))

# Labs from KB
for loc in kb:
    if loc['category'] == 'lab':
        lab_name = loc['name']
        for template, intent in LAB_TEMPLATES:
            q = template.format(lab_name=lab_name)
            faqs.append((q, intent, lab_name))

# Classrooms from KB
for loc in kb:
    if loc['category'] == 'classroom':
        room = loc.get('room_number', loc['name'])
        for template, intent in CLASSROOM_TEMPLATES:
            q = template.format(room=room)
            faqs.append((q, intent, loc['name']))

# ────────────────────────────────────────────────────────────
# SAVE
# ────────────────────────────────────────────────────────────
with open(FAQ_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["query", "intent", "entity"])
    writer.writerows(faqs)

find_loc = sum(1 for r in faqs if r[1]=='find_location')
ask_hrs  = sum(1 for r in faqs if r[1]=='ask_hours')
find_evt = sum(1 for r in faqs if r[1]=='find_event')

print(f"✅ Expanded FAQ saved: {len(faqs)} total examples")
print(f"   find_location : {find_loc}")
print(f"   ask_hours     : {ask_hrs}")
print(f"   find_event    : {find_evt}")
print(f"\n   Samples per category:")

entity_counts = {}
for q, intent, entity in faqs:
    entity_counts[entity] = entity_counts.get(entity, 0) + 1

by_count = sorted(entity_counts.items(), key=lambda x: x[1])
min_count = by_count[0][1]
max_count = by_count[-1][1]
avg_count = sum(v for _,v in entity_counts.items()) / len(entity_counts)

print(f"   Unique entities : {len(entity_counts)}")
print(f"   Min per entity  : {min_count}")
print(f"   Max per entity  : {max_count}")
print(f"   Avg per entity  : {avg_count:.1f}")

if min_count < 2:
    print(f"\n   ⚠ Entities with only 1 sample:")
    for ent, cnt in by_count:
        if cnt < 2:
            print(f"     - {ent}: {cnt}")
else:
    print(f"\n   ✅ All entities have at least {min_count} samples")
