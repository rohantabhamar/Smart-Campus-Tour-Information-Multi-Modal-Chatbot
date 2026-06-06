import streamlit as st
import streamlit.components.v1 as components
import sys
import json
from pathlib import Path
from datetime import datetime
from streamlit_folium import st_folium
from campus_map import build_campus_map

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from frontend.utils import call_text, call_audio, call_image, call_audio_text, call_multimodal

st.set_page_config(page_title="Campus Chatbot", page_icon="🏫", layout="wide")

HISTORY_FILE = Path(__file__).resolve().parent / "chat_history.json"

# ── Theme ─────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "light"

PIPELINE_COLORS = {
    "text":       "#4A90D9",
    "audio":      "#7B68EE",
    "image":      "#2ECC71",
    "audio-text": "#E67E22",
    "multimodal": "#E74C3C",
}

PIPELINE_ICONS = {
    "text":       "💬",
    "audio":      "🎵",
    "image":      "🖼️",
    "audio-text": "🎙️",
    "multimodal": "🔮",
}


# ── CSS for page ──────────────────────────────────────────────────────────
def get_css(theme: str) -> str:
    if theme == "dark":
        bg         = "#0E1117"
        text_color = "#FAFAFA"
        sub_color  = "#A0AEC0"
        user_bubble = "#2D3250"
    else:
        bg         = "#F8F9FA"
        text_color = "#1A202C"
        sub_color  = "#718096"
        user_bubble = "#EBF4FF"

    return f"""
    <style>
        .stApp {{ background-color: {bg}; }}
        .block-container {{ padding-top: 1rem; padding-bottom: 0; }}
        .user-bubble {{
            background: {user_bubble};
            border-radius: 16px 16px 4px 16px;
            padding: 12px 18px;
            margin-bottom: 12px;
            color: {text_color};
            font-size: 15px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        .section-title {{
            font-size: 22px;
            font-weight: 700;
            color: {text_color};
            margin-bottom: 4px;
        }}
        .section-sub {{
            font-size: 13px;
            color: {sub_color};
            margin-bottom: 16px;
        }}
    </style>
    """


# ── Response parser ────────────────────────────────────────────────────────
def parse_response(text: str):
    fields = {
        "LOCATION":   ("📍", "Location"),
        "FLOOR":      ("🏢", "Floor / Block"),
        "DIRECTIONS": ("🧭", "Directions"),
        "HOURS":      ("🕐", "Opening Hours"),
        "EVENTS":     ("🎉", "Events"),
        "ANSWER":     ("💬", "Answer"),
    }
    parsed = {key: None for key in fields}
    lines = text.strip().split("\n")
    for line in lines:
        for key in fields:
            if line.startswith(f"{key}:"):
                value = line[len(key)+1:].strip()
                if value and value.lower() != "n/a":
                    parsed[key] = value
                break
    return parsed, fields


def render_response_card(text: str, pipeline: str, latency: float):
    parsed, fields = parse_response(text)
    color = PIPELINE_COLORS.get(pipeline, "#4A90D9")
    icon  = PIPELINE_ICONS.get(pipeline, "💬")
    theme = st.session_state.get("theme", "light")

    if theme == "dark":
        card_bg     = "#1E2130"
        card_border = "#2D3250"
        text_color  = "#FAFAFA"
        sub_color   = "#A0AEC0"
        body_bg     = "#0E1117"
    else:
        card_bg     = "#FFFFFF"
        card_border = "#E2E8F0"
        text_color  = "#1A202C"
        sub_color   = "#718096"
        body_bg     = "#F8F9FA"

    card_rows = ""
    num_fields = 0
    for key, (emoji, label) in fields.items():
        if key == "ANSWER":
            continue
        value = parsed.get(key)
        if value:
            num_fields += 1
            card_rows += f"""
            <div class="card-row">
                <span class="card-icon">{emoji}</span>
                <span class="card-label">{label}</span>
                <span class="card-value">{value}</span>
            </div>"""

    answer = parsed.get("ANSWER") or text
    height = 140 + (num_fields * 52) + (len(answer) // 80 * 22)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: {body_bg};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    padding: 4px 2px 4px 2px;
  }}
  .chat-card {{
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 16px;
    padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .card-row {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid {card_border};
    font-size: 13px;
    color: {text_color};
  }}
  .card-icon {{ font-size: 15px; min-width: 22px; padding-top: 1px; }}
  .card-label {{
    font-weight: 700;
    min-width: 110px;
    color: {sub_color};
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    padding-top: 3px;
  }}
  .card-value {{ flex: 1; line-height: 1.55; color: {text_color}; }}
  .answer-section {{
    padding: 12px 0 8px 0;
    font-size: 14px;
    line-height: 1.65;
    color: {text_color};
    border-top: 1px solid {card_border};
    margin-top: 4px;
  }}
  .answer-icon {{ margin-right: 6px; }}
  .footer {{
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.6px;
    color: white;
    background: {color};
  }}
  .latency {{
    font-size: 11px;
    color: {sub_color};
  }}
</style>
</head>
<body>
<div class="chat-card">
  {card_rows}
  <div class="answer-section">
    <span class="answer-icon">💬</span>{answer}
  </div>
  <div class="footer">
    <span class="badge">{icon} {pipeline.upper()} PIPELINE</span>
    <span class="latency">⏱️ {latency}s</span>
  </div>
</div>
</body>
</html>"""

    components.html(html, height=height, scrolling=False)


# ── History ───────────────────────────────────────────────────────────────
def load_history() -> list:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_history(messages: list):
    HISTORY_FILE.write_text(json.dumps(messages, indent=2), encoding="utf-8")


if "messages" not in st.session_state:
    st.session_state.messages = load_history()

# ── Apply page CSS ─────────────────────────────────────────────────────────
st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/university.png", width=70)
    st.markdown("## Campus Chatbot")
    st.markdown("---")

    theme_label = "☀️ Light Mode" if st.session_state.theme == "dark" else "🌙 Dark Mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    st.markdown("---")
    st.markdown("### 🗺️ Campus Map")
    st.caption("Click any pin for details and sample questions.")
    campus_map = build_campus_map()
    st_folium(campus_map, width=300, height=380, returned_objects=[])

    st.markdown("---")
    st.markdown("### 📌 How it works")
    st.markdown("""
| Input | Pipeline |
|-------|----------|
| Text only | 💬 Text |
| Audio only | 🎵 Audio |
| Image only | 🖼️ Image |
| Audio + Text | 🎙️ Audio-Text |
| Any + Image | 🔮 Multimodal |
""")
    st.markdown("---")
    total = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.caption(f"💬 Total conversations: {total}")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        save_history([])
        st.rerun()

# ── Main ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🏫 Campus Navigation Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Ask about locations, directions, opening hours, and events.</div>', unsafe_allow_html=True)

# ── Input form ────────────────────────────────────────────────────────────
with st.form("input_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        text_query = st.text_input("💬 Text query", placeholder="Where is the library?")
    with col2:
        audio_file = st.file_uploader("🎵 Audio file", type=["wav", "mp3", "m4a"])
    with col3:
        image_file = st.file_uploader("🖼️ Image file", type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button("🚀 Send", use_container_width=True)

st.markdown("---")

# ── Current Q&A display ───────────────────────────────────────────────────
pairs = []
msgs  = st.session_state.messages
i     = 0
while i < len(msgs):
    if msgs[i]["role"] == "user" and i + 1 < len(msgs) and msgs[i+1]["role"] == "assistant":
        pairs.append((msgs[i], msgs[i+1]))
        i += 2
    else:
        i += 1

if pairs:
    user_msg, assistant_msg = pairs[-1]
    content = user_msg["content"]
    lines   = [l for l in content.split("\n") if l.startswith("💬")]
    display = lines[0].replace("💬 **", "").replace("**", "").strip() if lines else content
    st.markdown(f'<div class="user-bubble">🧑‍🎓 {display}</div>', unsafe_allow_html=True)
    render_response_card(
        text=assistant_msg["content"],
        pipeline=assistant_msg.get("pipeline", "text"),
        latency=assistant_msg.get("latency", 0),
    )

# ── Pipeline decision + API call ──────────────────────────────────────────
if submitted:
    has_text  = bool(text_query.strip())
    has_audio = audio_file is not None
    has_image = image_file is not None

    if not any([has_text, has_audio, has_image]):
        st.warning("Please provide at least one input.")
    else:
        parts = []
        if has_text:  parts.append(f"💬 **{text_query}**")
        if has_audio: parts.append(f"🎵 `{audio_file.name}`")
        if has_image: parts.append(f"🖼️ `{image_file.name}`")

        user_entry = {
            "role":    "user",
            "content": "\n".join(parts),
            "time":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.messages.append(user_entry)

        with st.spinner("Processing your request..."):
            if has_text and not has_audio and not has_image:
                result   = call_text(text_query)
                pipeline = "text"
            elif has_audio and not has_text and not has_image:
                result   = call_audio(audio_file)
                pipeline = "audio"
            elif has_image and not has_text and not has_audio:
                result   = call_image(image_file)
                pipeline = "image"
            elif has_audio and has_text and not has_image:
                result   = call_audio_text(audio_file, text_query)
                pipeline = "audio-text"
            else:
                result   = call_multimodal(
                    query      = text_query or None,
                    audio_file = audio_file or None,
                    image_file = image_file or None,
                )
                pipeline = "multimodal"

        answer = f"⚠️ {result['error']}" if result.get("error") else result.get("answer", "No response.")

        assistant_entry = {
            "role":     "assistant",
            "content":  answer,
            "pipeline": pipeline,
            "latency":  result.get("latency", 0),
            "time":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.messages.append(assistant_entry)
        save_history(st.session_state.messages)
        st.rerun()
