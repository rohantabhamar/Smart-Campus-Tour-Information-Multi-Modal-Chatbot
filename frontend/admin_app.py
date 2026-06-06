import streamlit as st
import sys
import time
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from frontend.utils import get_health

st.set_page_config(page_title="Admin Dashboard", page_icon="⚙️", layout="wide")

LOG_DIR   = Path(__file__).resolve().parent.parent / "logs" / "dev"
APP_LOG   = LOG_DIR / "app.log"
ERROR_LOG = LOG_DIR / "error.log"
HISTORY   = Path(__file__).resolve().parent / "chat_history.json"

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Admin Panel")
    st.markdown("---")
    refresh = st.slider("Auto refresh (sec)", 5, 60, 15)
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

st.title("⚙️ Campus Chatbot — Admin Dashboard")
st.markdown("---")

# ── Row 1 — Health metrics ────────────────────────────────────────────────
health  = get_health()
status  = health.get("status", "unknown")
env     = health.get("env", "dev")
models  = {k: v for k, v in health.get("models", {}).items() if k != "status"}
ok_count   = sum(1 for v in models.values() if v == "ok")
fail_count = len(models) - ok_count

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("System Status", "🟢 Healthy" if "healthy" in status else "🔴 Unhealthy")
with col2:
    st.metric("Environment", env.upper())
with col3:
    st.metric("Models OK", f"{ok_count}/{len(models)}")
with col4:
    # count total queries from log
    total_queries = 0
    if APP_LOG.exists():
        total_queries = sum(1 for l in APP_LOG.read_text(encoding="utf-8").splitlines() if "endpoint →" in l)
    st.metric("Total Queries", total_queries)

st.markdown("---")

# ── Row 2 — Model status + Pipeline breakdown ─────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🤖 Model Status")
    for model, status in models.items():
        if status == "ok":
            st.success(f"✅ {model}")
        else:
            st.error(f"❌ {model} — {status}")

with col_right:
    st.subheader("📊 Pipeline Usage")
    if APP_LOG.exists():
        lines    = APP_LOG.read_text(encoding="utf-8").splitlines()
        pipeline_counts = Counter()
        for line in lines:
            if "text endpoint" in line:       pipeline_counts["text"] += 1
            elif "audio-text endpoint" in line: pipeline_counts["audio-text"] += 1
            elif "audio endpoint" in line:    pipeline_counts["audio"] += 1
            elif "image endpoint" in line:    pipeline_counts["image"] += 1
            elif "multimodal endpoint" in line: pipeline_counts["multimodal"] += 1

        if pipeline_counts:
            df = pd.DataFrame(
                pipeline_counts.items(),
                columns=["Pipeline", "Count"]
            ).sort_values("Count", ascending=False)
            st.bar_chart(df.set_index("Pipeline"))
        else:
            st.info("No pipeline data yet.")

st.markdown("---")

# ── Row 3 — Response times ────────────────────────────────────────────────
st.subheader("⏱️ Average Response Times per Node")
if APP_LOG.exists():
    timing_data = {}
    for line in APP_LOG.read_text(encoding="utf-8").splitlines():
        if "duration=" in line:
            try:
                node     = line.split("] [")[-1].split("]")[0]
                duration = float(line.split("duration=")[1].split("s")[0])
                timing_data.setdefault(node, []).append(duration)
            except:
                pass
    if timing_data:
        avg_times = {k: round(sum(v)/len(v), 3) for k, v in timing_data.items()}
        df = pd.DataFrame(avg_times.items(), columns=["Node", "Avg (s)"]).sort_values("Avg (s)", ascending=False)
        st.bar_chart(df.set_index("Node"))
    else:
        st.info("No timing data yet.")

st.markdown("---")

# ── Row 4 — Recent queries table ─────────────────────────────────────────
st.subheader("📋 Recent Queries")
if APP_LOG.exists():
    lines       = APP_LOG.read_text(encoding="utf-8").splitlines()
    query_lines = [l for l in lines if "endpoint →" in l][-15:]
    if query_lines:
        rows = []
        for line in reversed(query_lines):
            try:
                timestamp = line.split("]")[0].strip("[")
                pipeline  = line.split("[api.routes.")[-1].split("]")[0] if "[api.routes." in line else "unknown"
                query     = line.split("→")[-1].strip()
                rows.append({"Time": timestamp, "Pipeline": pipeline, "Query": query})
            except:
                rows.append({"Time": "", "Pipeline": "", "Query": line})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No queries logged yet.")

st.markdown("---")

# ── Row 5 — Chat history stats ────────────────────────────────────────────
st.subheader("💬 Chat History")
if HISTORY.exists():
    try:
        history = json.loads(HISTORY.read_text(encoding="utf-8"))
        user_msgs = [m for m in history if m["role"] == "user"]
        st.metric("Total conversations stored", len(user_msgs))
        if user_msgs:
            st.markdown("**Last 5 user queries:**")
            for msg in reversed(user_msgs[-5:]):
                st.markdown(f"- `{msg.get('time', '')}` — {msg['content'][:80]}")
    except:
        st.info("Could not read chat history.")
else:
    st.info("No chat history yet.")

st.markdown("---")

# ── Row 6 — Errors ────────────────────────────────────────────────────────
st.subheader("🚨 Recent Errors")
if ERROR_LOG.exists():
    error_lines = [
        l for l in ERROR_LOG.read_text(encoding="utf-8").splitlines()
        if "unittest" not in l and "mock" not in l and "side_effect" not in l
        and "[ERROR]" in l
    ][-5:]
    if error_lines:
        for line in reversed(error_lines):
            st.error(line)
    else:
        st.success("✅ No real errors logged.")
else:
    st.success("✅ No error log found — system is clean.")

# ── Auto refresh ──────────────────────────────────────────────────────────
time.sleep(refresh)
st.rerun()