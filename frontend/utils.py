import requests
import time
from pathlib import Path

API_BASE = "http://127.0.0.1:8000"


def call_text(query: str) -> dict:
    t0 = time.perf_counter()
    r  = requests.post(f"{API_BASE}/query/text", json={"query": query})
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}


def call_audio(audio_path: str) -> dict:
    t0 = time.perf_counter()
    with open(audio_path, "rb") as f:
        r = requests.post(f"{API_BASE}/query/audio", files={"file": f})
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}


def call_image(image_path: str) -> dict:
    t0 = time.perf_counter()
    with open(image_path, "rb") as f:
        r = requests.post(f"{API_BASE}/query/image", files={"file": f})
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}


def call_audio_text(audio_path: str, text_query: str = None) -> dict:
    t0 = time.perf_counter()
    with open(audio_path, "rb") as f:
        data  = {"text_query": text_query} if text_query else {}
        r = requests.post(f"{API_BASE}/query/audio-text", files={"file": f}, data=data)
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}


def call_multimodal(query: str = None, audio_path: str = None, image_path: str = None) -> dict:
    t0    = time.perf_counter()
    files = {}
    data  = {}
    if query:
        data["query"] = query
    if audio_path and Path(audio_path).exists():
        files["audio_file"] = open(audio_path, "rb")
    if image_path and Path(image_path).exists():
        files["image_file"] = open(image_path, "rb")
    r = requests.post(f"{API_BASE}/query/multimodal", files=files, data=data)
    for f in files.values():
        f.close()
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}


def get_health() -> dict:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        return r.json()
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}