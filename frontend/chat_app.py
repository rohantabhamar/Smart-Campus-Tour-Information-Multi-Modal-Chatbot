import streamlit as st
import sys
import json
from pathlib import Path
from datetime import datetime
import folium
from streamlit_folium import st_folium
from campus_map import build_campus_map


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from frontend.utils import call_text, call_audio, call_image, call_audio_text, call_multimodal

# ── Config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Campus Chatbot", page_icon="🏫", layout="wide")

HISTORY_FILE = Path(__file__).resolve().parent / "chat_history.json"

# ── History persistence ───────────────────────────────────────────────────
def load_history() -> list:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except:
            return []
    return []

def save_history(messages: list):
    HISTORY_FILE.write_text(json.dumps(messages, indent=2), encoding="utf-8")

# ── Session state ─────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

# ── Layout ────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 0rem; }
        .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
        .stCaption { color: #888; font-size: 0.75rem; }
    </style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/university.png", width=80)
    st.title("Campus Chatbot")
    st.markdown("---")
    
    st.markdown("### 🗺️ Campus Map")
    st.caption("Click any pin to see details and sample questions.")
    campus_map = build_campus_map()
    st_folium(campus_map, width=300, height=400, returned_objects=[])

    st.markdown("---")
    st.markdown("### 📌 How it works")
    st.markdown("""
    Fill in any input and hit **Send**:

    | Input | Pipeline |
    |-------|----------|
    | Text only | Text |
    | Audio only | Audio |
    | Image only | Image |
    | Audio + Text | Audio-Text |
    | Any + Image | Multimodal |
    """)
    st.markdown("---")
    st.markdown(f"**💬 Total conversations:** {len([m for m in st.session_state.messages if m['role'] == 'user'])}")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        save_history([])
        st.rerun()
    
    

# ── Main area ─────────────────────────────────────────────────────────────
st.title("🏫 Campus Navigation Assistant")
st.caption("Ask about locations, directions, opening hours, and events.")
st.markdown("---")

# ── Input form — always on top ────────────────────────────────────────────
with st.form("input_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        text_query = st.text_input("💬 Text query", placeholder="Where is the library?")
    with col2:
        audio_path = st.text_input("🎵 Audio file path", placeholder="E:/path/to/audio.wav")
    with col3:
        image_path = st.text_input("🖼️ Image file path", placeholder="E:/path/to/image.jpg")
    submitted = st.form_submit_button("🚀 Send", use_container_width=True)

st.markdown("---")

# ── Chat history — scrollable container below input ───────────────────────
chat_container = st.container(height=500)
with chat_container:
    # show only user query and assistant answer — nothing else
    pairs = []
    msgs  = st.session_state.messages
    i     = 0
    while i < len(msgs):
        if msgs[i]["role"] == "user" and i + 1 < len(msgs) and msgs[i+1]["role"] == "assistant":
            pairs.append((msgs[i], msgs[i+1]))
            i += 2
        else:
            i += 1

    pairs = pairs[-1:] if pairs else []
    for user_msg, assistant_msg in pairs:
        with st.chat_message("user"):
            # show only text query — strip emoji prefixes
            content = user_msg["content"]
            lines   = [l for l in content.split("\n") if l.startswith("💬")]
            display = lines[0].replace("💬 **", "").replace("**", "").strip() if lines else content
            st.markdown(display)

        with st.chat_message("assistant"):
            st.markdown(assistant_msg["content"])

# ── Pipeline decision + API call ──────────────────────────────────────────
if submitted:
    has_text  = bool(text_query.strip())
    has_audio = bool(audio_path.strip())
    has_image = bool(image_path.strip())

    if not any([has_text, has_audio, has_image]):
        st.warning("Please provide at least one input.")
    else:
        # Build user message
        parts = []
        if has_text:  parts.append(f"💬 **{text_query}**")
        if has_audio: parts.append(f"🎵 `{audio_path}`")
        if has_image: parts.append(f"🖼️ `{image_path}`")

        user_entry = {
            "role":       "user",
            "content":    "\n".join(parts),
            "image_path": image_path if has_image else None,
            "time":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.messages.append(user_entry)

        # Call API
        with st.spinner("Processing your request..."):
            if has_text and not has_audio and not has_image:
                result   = call_text(text_query)
                pipeline = "text"
            elif has_audio and not has_text and not has_image:
                result   = call_audio(audio_path)
                pipeline = "audio"
            elif has_image and not has_text and not has_audio:
                result   = call_image(image_path)
                pipeline = "image"
            elif has_audio and has_text and not has_image:
                result   = call_audio_text(audio_path, text_query)
                pipeline = "audio-text"
            else:
                result   = call_multimodal(
                    query      = text_query or None,
                    audio_path = audio_path or None,
                    image_path = image_path or None,
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