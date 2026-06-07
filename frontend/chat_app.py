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

st.set_page_config(
    page_title="Campus Navigator AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

HISTORY_FILE = Path(__file__).resolve().parent / "chat_history.json"

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

PIPELINE_COLORS = {
    "text":       "#6C63FF",
    "audio":      "#FF6584",
    "image":      "#43E97B",
    "audio-text": "#F093FB",
    "multimodal": "#4FACFE",
}

PIPELINE_ICONS = {
    "text":       "💬",
    "audio":      "🎵",
    "image":      "🖼️",
    "audio-text": "🎙️",
    "multimodal": "🔮",
}

PIPELINE_GRADIENTS = {
    "text":       "linear-gradient(135deg, #6C63FF, #3B37CC)",
    "audio":      "linear-gradient(135deg, #FF6584, #CC3354)",
    "image":      "linear-gradient(135deg, #43E97B, #38F9D7)",
    "audio-text": "linear-gradient(135deg, #F093FB, #F5576C)",
    "multimodal": "linear-gradient(135deg, #4FACFE, #00F2FE)",
}


def get_css(theme: str) -> str:
    if theme == "dark":
        bg          = "#0A0B0F"
        sidebar_bg  = "#111318"
        card_bg     = "#16181F"
        card_border = "#252836"
        text_color  = "#E8E9F0"
        sub_color   = "#8B8FA8"
        input_bg    = "#1C1E27"
        input_border= "#2D3047"
        user_bg     = "#1E2040"
        user_border = "#3D4070"
        accent      = "#6C63FF"
        divider     = "#1E2030"
        tag_bg      = "#1C1E2A"
    else:
        bg          = "#F0F2F8"
        sidebar_bg  = "#FFFFFF"
        card_bg     = "#FFFFFF"
        card_border = "#E2E5F0"
        text_color  = "#1A1D2E"
        sub_color   = "#6B7280"
        input_bg    = "#FFFFFF"
        input_border= "#D1D5DB"
        user_bg     = "#EEF2FF"
        user_border = "#C7D2FE"
        accent      = "#6C63FF"
        divider     = "#E5E7EB"
        tag_bg      = "#F3F4F6"

    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, .stApp {{
            background-color: {bg} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background: {sidebar_bg} !important;
            border-right: 1px solid {card_border} !important;
        }}
        section[data-testid="stSidebar"] > div {{
            padding-top: 1.5rem !important;
        }}

        /* ── Main container ── */
        .block-container {{
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            max-width: 100% !important;
        }}

        /* ── Header banner ── */
        .app-header {{
            background: linear-gradient(135deg, #6C63FF 0%, #4FACFE 50%, #43E97B 100%);
            padding: 28px 36px 22px 36px;
            border-radius: 0 0 24px 24px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
        }}
        .app-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 300px;
            height: 300px;
            background: rgba(255,255,255,0.05);
            border-radius: 50%;
        }}
        .app-header::after {{
            content: '';
            position: absolute;
            bottom: -60%;
            right: 10%;
            width: 200px;
            height: 200px;
            background: rgba(255,255,255,0.05);
            border-radius: 50%;
        }}
        .header-title {{
            font-size: 28px;
            font-weight: 700;
            color: white;
            margin: 0;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .header-sub {{
            font-size: 14px;
            color: rgba(255,255,255,0.8);
            margin-top: 6px;
            font-weight: 400;
        }}
        .header-badges {{
            display: flex;
            gap: 8px;
            margin-top: 14px;
            flex-wrap: wrap;
        }}
        .header-badge {{
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.25);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            backdrop-filter: blur(10px);
        }}

        /* ── Input form ── */
        .input-section {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 20px;
            padding: 20px 24px;
            margin: 0 0 20px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .input-label {{
            font-size: 11px;
            font-weight: 700;
            color: {sub_color};
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}

        /* ── Streamlit input overrides ── */
        .stTextInput > div > div > input {{
            background: {input_bg} !important;
            border: 1.5px solid {input_border} !important;
            border-radius: 12px !important;
            color: {text_color} !important;
            font-size: 14px !important;
            padding: 12px 16px !important;
            font-family: 'Inter', sans-serif !important;
        }}
        .stTextInput > div > div > input:focus {{
            border-color: {accent} !important;
            box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.15) !important;
        }}
        .stFileUploader {{
            background: {input_bg} !important;
            border: 1.5px dashed {input_border} !important;
            border-radius: 12px !important;
        }}
        .stFileUploader:hover {{
            border-color: {accent} !important;
        }}

        /* ── Send button ── */
        .stFormSubmitButton > button {{
            background: linear-gradient(135deg, #6C63FF, #4FACFE) !important;
            color: white !important;
            border: none !important;
            border-radius: 14px !important;
            padding: 14px 32px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            letter-spacing: 0.3px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(108, 99, 255, 0.4) !important;
            width: 100% !important;
        }}
        .stFormSubmitButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(108, 99, 255, 0.5) !important;
        }}

        /* ── Sidebar buttons ── */
        .stButton > button {{
            background: {tag_bg} !important;
            border: 1px solid {card_border} !important;
            border-radius: 10px !important;
            color: {text_color} !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }}
        .stButton > button:hover {{
            border-color: {accent} !important;
            color: {accent} !important;
        }}

        /* ── User message ── */
        .user-message {{
            display: flex;
            justify-content: flex-end;
            margin-bottom: 16px;
        }}
        .user-bubble {{
            background: linear-gradient(135deg, #6C63FF, #4FACFE);
            color: white;
            border-radius: 20px 20px 4px 20px;
            padding: 14px 20px;
            max-width: 70%;
            font-size: 15px;
            font-family: 'Inter', sans-serif;
            line-height: 1.5;
            box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
        }}
        .user-label {{
            font-size: 11px;
            color: {sub_color};
            text-align: right;
            margin-bottom: 6px;
            font-weight: 500;
        }}

        /* ── Section labels ── */
        .stMarkdown h3 {{
            color: {text_color} !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }}

        /* ── Dividers ── */
        hr {{
            border-color: {divider} !important;
            margin: 12px 0 !important;
        }}

        /* ── Sidebar caption ── */
        .stCaption {{
            color: {sub_color} !important;
            font-size: 12px !important;
        }}

        /* ── Hide Streamlit branding ── */
        #MainMenu, footer, header {{ visibility: hidden; }}
        .stDeployButton {{ display: none; }}

        /* ── Scrollbar ── */
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: {bg}; }}
        ::-webkit-scrollbar-thumb {{ background: {card_border}; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: {sub_color}; }}
    </style>
    """


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
    gradient = PIPELINE_GRADIENTS.get(pipeline, "linear-gradient(135deg, #6C63FF, #4FACFE)")
    icon = PIPELINE_ICONS.get(pipeline, "💬")
    theme = st.session_state.get("theme", "dark")

    if theme == "dark":
        card_bg     = "#16181F"
        card_border = "#252836"
        text_color  = "#E8E9F0"
        sub_color   = "#8B8FA8"
        body_bg     = "#0A0B0F"
        row_hover   = "#1C1E2A"
    else:
        card_bg     = "#FFFFFF"
        card_border = "#E2E5F0"
        text_color  = "#1A1D2E"
        sub_color   = "#6B7280"
        body_bg     = "#F0F2F8"
        row_hover   = "#F9FAFB"

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
                <div class="icon-wrap">{emoji}</div>
                <div class="row-content">
                    <div class="row-label">{label}</div>
                    <div class="row-value">{value}</div>
                </div>
            </div>"""

    answer = parsed.get("ANSWER") or text
    height = 180 + (num_fields * 68) + (len(answer) // 70 * 22)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: {body_bg};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
    padding: 4px 2px;
  }}
  .bot-label {{
    font-size: 11px;
    color: {sub_color};
    font-weight: 600;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
  }}
  .chat-card {{
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 4px 20px 20px 20px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  }}
  .card-header {{
    background: {gradient};
    padding: 12px 18px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .card-header-icon {{
    font-size: 18px;
  }}
  .card-header-text {{
    font-size: 13px;
    font-weight: 700;
    color: white;
    letter-spacing: 0.5px;
  }}
  .card-header-badge {{
    margin-left: auto;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.3);
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
  }}
  .card-body {{
    padding: 4px 0;
  }}
  .card-row {{
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 10px 18px;
    border-bottom: 1px solid {card_border};
    transition: background 0.15s;
  }}
  .card-row:hover {{ background: {row_hover}; }}
  .icon-wrap {{
    font-size: 18px;
    min-width: 28px;
    padding-top: 2px;
    text-align: center;
  }}
  .row-content {{ flex: 1; }}
  .row-label {{
    font-size: 9px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: {sub_color};
    margin-bottom: 3px;
  }}
  .row-value {{
    font-size: 13px;
    line-height: 1.55;
    color: {text_color};
  }}
  .answer-section {{
    padding: 14px 18px;
    font-size: 14px;
    line-height: 1.7;
    color: {text_color};
  }}
  .answer-intro {{
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: {sub_color};
    margin-bottom: 6px;
  }}
  .answer-text {{
    font-size: 14px;
    line-height: 1.7;
    color: {text_color};
  }}
  .card-footer {{
    padding: 10px 18px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-top: 1px solid {card_border};
  }}
  .latency {{
    font-size: 11px;
    color: {sub_color};
    margin-left: auto;
  }}
</style>
</head>
<body>
<div class="bot-label">🤖 CAMPUS AI</div>
<div class="chat-card">
  <div class="card-header">
    <span class="card-header-icon">{icon}</span>
    <span class="card-header-text">{pipeline.upper()} PIPELINE</span>
    <span class="card-header-badge">AI Response</span>
  </div>
  <div class="card-body">
    {card_rows}
    <div class="answer-section">
      <div class="answer-intro">💡 Summary</div>
      <div class="answer-text">{answer}</div>
    </div>
  </div>
  <div class="card-footer">
    <span class="latency">⏱️ Response time: {latency}s</span>
  </div>
</div>
</body>
</html>"""

    components.html(html, height=height, scrolling=False)


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

st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 0 0 16px 0;">
        <div style="font-size: 48px; margin-bottom: 8px;">🎓</div>
        <div style="font-size: 18px; font-weight: 700; letter-spacing: -0.3px;">Campus Navigator</div>
        <div style="font-size: 12px; color: #8B8FA8; margin-top: 4px;">Powered by AI</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    theme_label = "☀️ Switch to Light" if st.session_state.theme == "dark" else "🌙 Switch to Dark"
    if st.button(theme_label, use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    st.divider()

    st.markdown("**🗺️ Campus Map**")
    st.caption("Click any pin for details and sample questions.")
    campus_map = build_campus_map()
    st_folium(campus_map, width=290, height=340, returned_objects=[])

    st.divider()

    st.markdown("**⚡ Smart Pipeline Selection**")
    theme = st.session_state.theme
    tc = "#E8E9F0" if theme == "dark" else "#1A1D2E"
    bc = "#1C1E2A" if theme == "dark" else "#F3F4F6"
    bd = "#252836" if theme == "dark" else "#E2E5F0"
    st.markdown(f"""
    <div style="font-size:12px; line-height:2;">
        <div style="background:{bc}; border:1px solid {bd}; border-radius:8px; padding:10px 14px; margin-bottom:4px;">
            💬 <b>Text only</b> → Text Pipeline
        </div>
        <div style="background:{bc}; border:1px solid {bd}; border-radius:8px; padding:10px 14px; margin-bottom:4px;">
            🎵 <b>Audio only</b> → Audio Pipeline
        </div>
        <div style="background:{bc}; border:1px solid {bd}; border-radius:8px; padding:10px 14px; margin-bottom:4px;">
            🖼️ <b>Image only</b> → Image Pipeline
        </div>
        <div style="background:{bc}; border:1px solid {bd}; border-radius:8px; padding:10px 14px; margin-bottom:4px;">
            🎙️ <b>Audio + Text</b> → Audio-Text Pipeline
        </div>
        <div style="background:{bc}; border:1px solid {bd}; border-radius:8px; padding:10px 14px;">
            🔮 <b>Any + Image</b> → Multimodal Pipeline
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    total = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.caption(f"📊 Total conversations: {total}")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        save_history([])
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="header-title">🎓 Smart Campus Navigator AI</div>
    <div class="header-sub">Ask me anything about campus — locations, directions, hours, and events</div>
    <div class="header-badges">
        <span class="header-badge">💬 Text</span>
        <span class="header-badge">🎵 Voice</span>
        <span class="header-badge">🖼️ Image</span>
        <span class="header-badge">🔮 Multimodal</span>
        <span class="header-badge">154 Locations</span>
        <span class="header-badge">5 AI Pipelines</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input form ────────────────────────────────────────────────────────────
with st.form("input_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        text_query = st.text_input(
            "💬 Ask anything about campus",
            placeholder="e.g. Where is the library? What time does the cafeteria open?",
            label_visibility="collapsed"
        )
    with col2:
        audio_file = st.file_uploader("🎵 Voice query", type=["wav", "mp3", "m4a"], label_visibility="visible")
    with col3:
        image_file = st.file_uploader("🖼️ Campus image", type=["jpg", "jpeg", "png"], label_visibility="visible")

    submitted = st.form_submit_button("🚀 Send to Campus AI", use_container_width=True)

# ── Current Q&A ───────────────────────────────────────────────────────────
pairs = []
msgs = st.session_state.messages
i = 0
while i < len(msgs):
    if msgs[i]["role"] == "user" and i + 1 < len(msgs) and msgs[i+1]["role"] == "assistant":
        pairs.append((msgs[i], msgs[i+1]))
        i += 2
    else:
        i += 1

if pairs:
    user_msg, assistant_msg = pairs[-1]
    content = user_msg["content"]
    lines = [l for l in content.split("\n") if l.startswith("💬")]
    display = lines[0].replace("💬 **", "").replace("**", "").strip() if lines else content

    st.markdown(f"""
    <div class="user-label">You</div>
    <div class="user-message">
        <div class="user-bubble">🧑‍🎓 {display}</div>
    </div>
    """, unsafe_allow_html=True)

    render_response_card(
        text=assistant_msg["content"],
        pipeline=assistant_msg.get("pipeline", "text"),
        latency=assistant_msg.get("latency", 0),
    )

elif not pairs:
    theme = st.session_state.theme
    card_bg = "#16181F" if theme == "dark" else "#FFFFFF"
    border = "#252836" if theme == "dark" else "#E2E5F0"
    tc = "#E8E9F0" if theme == "dark" else "#1A1D2E"
    sc = "#8B8FA8" if theme == "dark" else "#6B7280"
    st.markdown(f"""
    <div style="text-align:center; padding: 40px 20px; background:{card_bg};
                border:1px solid {border}; border-radius:20px; margin-top:10px;">
        <div style="font-size:56px; margin-bottom:16px;">🎓</div>
        <div style="font-size:20px; font-weight:700; color:{tc}; margin-bottom:8px;">
            Welcome to Campus Navigator AI
        </div>
        <div style="font-size:14px; color:{sc}; max-width:500px; margin:0 auto; line-height:1.7;">
            Ask me about any campus location — type your question, upload a voice recording,
            or share an image of a campus building. I'll identify it and give you directions,
            opening hours, and upcoming events.
        </div>
        <div style="display:flex; justify-content:center; gap:12px; margin-top:24px; flex-wrap:wrap;">
            <span style="background:linear-gradient(135deg,#6C63FF,#4FACFE); color:white;
                         padding:8px 18px; border-radius:20px; font-size:12px; font-weight:600;">
                💬 "Where is the library?"
            </span>
            <span style="background:linear-gradient(135deg,#43E97B,#38F9D7); color:white;
                         padding:8px 18px; border-radius:20px; font-size:12px; font-weight:600;">
                🕐 "When does the gym open?"
            </span>
            <span style="background:linear-gradient(135deg,#F093FB,#F5576C); color:white;
                         padding:8px 18px; border-radius:20px; font-size:12px; font-weight:600;">
                🎉 "Any events this week?"
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Pipeline logic ─────────────────────────────────────────────────────────
if submitted:
    has_text = bool(text_query.strip())
    has_audio = audio_file is not None
    has_image = image_file is not None

    if not any([has_text, has_audio, has_image]):
        st.warning("Please provide at least one input — text, audio, or image.")
    else:
        parts = []
        if has_text:  parts.append(f"💬 **{text_query}**")
        if has_audio: parts.append(f"🎵 `{audio_file.name}`")
        if has_image: parts.append(f"🖼️ `{image_file.name}`")

        st.session_state.messages.append({
            "role":    "user",
            "content": "\n".join(parts),
            "time":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        with st.spinner("🤖 Campus AI is thinking..."):
            if has_text and not has_audio and not has_image:
                result, pipeline = call_text(text_query), "text"
            elif has_audio and not has_text and not has_image:
                result, pipeline = call_audio(audio_file), "audio"
            elif has_image and not has_text and not has_audio:
                result, pipeline = call_image(image_file), "image"
            elif has_audio and has_text and not has_image:
                result, pipeline = call_audio_text(audio_file, text_query), "audio-text"
            else:
                result = call_multimodal(
                    query=text_query or None,
                    audio_file=audio_file or None,
                    image_file=image_file or None,
                )
                pipeline = "multimodal"

        answer = f"⚠️ {result['error']}" if result.get("error") else result.get("answer", "No response.")

        st.session_state.messages.append({
            "role":     "assistant",
            "content":  answer,
            "pipeline": pipeline,
            "latency":  result.get("latency", 0),
            "time":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        save_history(st.session_state.messages)
        st.rerun()
