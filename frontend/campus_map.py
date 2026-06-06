"""
frontend/campus_map.py
----------------------
Builds an interactive campus map from campus_kb.json.
Shows unique building-level locations with color-coded markers.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import folium
from pathlib import Path

KB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_kb.json"

# ── Category colors ───────────────────────────────────────────────────────
CATEGORY_COLORS = {
    "library":          "blue",
    "cafeteria":        "orange",
    "gym":              "green",
    "it_lab":           "purple",
    "admin_office":     "red",
    "career_center":    "darkred",
    "medical_center":   "lightred",
    "auditorium":       "cadetblue",
    "seminar_room":     "lightblue",
    "student_union":    "beige",
    "lecture_hall":     "darkblue",
    "printing_room":    "gray",
    "security_office":  "black",
    "outdoor":          "lightgreen",
    "engineering_college": "darkgreen",
    "department":       "darkpurple",
}

# ── Sample questions per category ─────────────────────────────────────────
SAMPLE_QUESTIONS = {
    "library":          "What are the library opening hours?",
    "cafeteria":        "What food options are available in the cafeteria?",
    "gym":              "What are the gym timings?",
    "it_lab":           "Where is the IT lab and what equipment does it have?",
    "admin_office":     "How do I reach the admissions office?",
    "career_center":    "What services does the career centre offer?",
    "medical_center":   "Where is the medical centre?",
    "auditorium":       "What events are happening at the auditorium?",
    "seminar_room":     "How do I book a seminar room?",
    "student_union":    "What events are at the student union?",
    "lecture_hall":     "Where is Lecture Hall A?",
    "printing_room":    "Where can I print documents?",
    "security_office":  "Where is campus security?",
    "outdoor":          "Where is the campus garden?",
    "engineering_college": "Where is the engineering block?",
    "department":       "Where is the mechanical engineering department?",
}


def build_campus_map() -> folium.Map:
    """Build and return a folium map with all campus locations."""
    kb = json.loads(KB_PATH.read_text(encoding="utf-8"))

    # ── Filter to unique building-level entries only ───────────────────────
    # Skip individual classrooms, labs, teachers rooms, hod offices
    # These are all inside the Engineering Block which has its own entry
    skip_categories = {"classroom", "lab", "teachers_room", "hod_office"}
    unique_entries  = [e for e in kb if e["category"] not in skip_categories]

    # Centre map on campus centroid
    avg_lat = sum(e["coordinates"]["lat"] for e in unique_entries) / len(unique_entries)
    avg_lng = sum(e["coordinates"]["lng"] for e in unique_entries) / len(unique_entries)
    campus_map = folium.Map(location=[avg_lat, avg_lng], zoom_start=16, tiles="CartoDB positron")

    # ── Add markers ───────────────────────────────────────────────────────
    for entry in unique_entries:
        lat      = entry["coordinates"]["lat"]
        lng      = entry["coordinates"]["lng"]
        name     = entry["name"]
        category = entry["category"]
        desc     = entry.get("description", "")
        hours    = entry.get("opening_hours", {})
        events   = entry.get("events", [])
        sample_q = SAMPLE_QUESTIONS.get(category, f"Tell me about {name}")
        color    = CATEGORY_COLORS.get(category, "blue")

        # Build hours HTML
        hours_html = "".join(
            f"<tr><td><b>{day}</b></td><td>{time}</td></tr>"
            for day, time in hours.items()
        ) if hours else "<tr><td colspan='2'>Hours not available</td></tr>"

        # Build events HTML
        events_html = "".join(f"<li>{e}</li>" for e in events) if events else "<li>No upcoming events</li>"

        # Floor map for Engineering Block
        floor_map = entry.get("floor_map", {})
        floor_html = ""
        if floor_map:
            floor_html = "<br><b>Floors:</b><ul>" + "".join(
                f"<li><b>{floor}:</b> {dept}</li>"
                for floor, dept in floor_map.items()
            ) + "</ul>"

        popup_html = f"""
        <div style="width:280px; font-family:Arial,sans-serif; font-size:13px;">
            <h4 style="margin:0 0 6px 0; color:#1a1a2e;">{name}</h4>
            <p style="margin:0 0 8px 0; color:#555; font-size:12px;">{desc[:150]}{'...' if len(desc)>150 else ''}</p>
            {floor_html}
            <details>
                <summary style="cursor:pointer; color:#0066cc; font-size:12px;">📅 Opening Hours</summary>
                <table style="font-size:11px; width:100%; margin-top:4px;">
                    {hours_html}
                </table>
            </details>
            <details style="margin-top:4px;">
                <summary style="cursor:pointer; color:#0066cc; font-size:12px;">🎉 Events</summary>
                <ul style="font-size:11px; margin:4px 0 0 0; padding-left:16px;">
                    {events_html}
                </ul>
            </details>
            <div style="margin-top:8px; padding:6px; background:#f0f7ff; border-radius:4px; font-size:11px; color:#333;">
                💬 <b>Try asking:</b><br><i>"{sample_q}"</i>
            </div>
        </div>
        """

        folium.Marker(
            location  = [lat, lng],
            popup     = folium.Popup(popup_html, max_width=300),
            tooltip   = name,
            icon      = folium.Icon(color=color, icon="info-sign"),
        ).add_to(campus_map)

    # ── Legend ────────────────────────────────────────────────────────────
    legend_html = """
    <div style="position:fixed; bottom:30px; left:30px; z-index:9999;
                background:white; padding:12px; border-radius:8px;
                border:1px solid #ccc; font-size:12px; font-family:Arial;">
        <b>📍 Campus Legend</b><br>
        <span style="color:#2A81CB;">●</span> Library / IT Lab<br>
        <span style="color:#FF8000;">●</span> Cafeteria / Food<br>
        <span style="color:#2AAD27;">●</span> Sports / Outdoor<br>
        <span style="color:#9C2BCB;">●</span> Departments<br>
        <span style="color:#CB2B3E;">●</span> Admin Offices<br>
        <span style="color:#3D9970;">●</span> Engineering Block<br>
        <span style="color:#3D6B6B;">●</span> Auditorium / Events<br>
    </div>
    """
    campus_map.get_root().html.add_child(folium.Element(legend_html))

    return campus_map