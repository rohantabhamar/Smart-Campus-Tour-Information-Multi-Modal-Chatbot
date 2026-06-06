import requests
import time

import os
API_BASE = os.getenv("API_BASE", "http://campus_api:8000")


def call_text(query: str) -> dict:
    t0 = time.perf_counter()
    r  = requests.post(f"{API_BASE}/query/text", json={"query": query})
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}


def call_audio(audio_file) -> dict:
    t0 = time.perf_counter()
    r  = requests.post(
        f"{API_BASE}/query/audio",
        files={"file": (audio_file.name, audio_file.getvalue(), "audio/wav")}
    )
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}


def call_image(image_file) -> dict:
    t0 = time.perf_counter()
    r  = requests.post(
        f"{API_BASE}/query/image",
        files={"file": (image_file.name, image_file.getvalue(), "image/jpeg")}
    )
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}


def call_audio_text(audio_file, text_query: str = None) -> dict:
    t0   = time.perf_counter()
    data = {"text_query": text_query} if text_query else {}
    r    = requests.post(
        f"{API_BASE}/query/audio-text",
        files={"file": (audio_file.name, audio_file.getvalue(), "audio/wav")},
        data=data
    )
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}


def call_multimodal(query=None, audio_file=None, image_file=None) -> dict:
    t0    = time.perf_counter()
    files = {}
    data  = {}
    if query:
        data["query"] = query
    if audio_file:
        files["audio_file"] = (audio_file.name, audio_file.getvalue(), "audio/wav")
    if image_file:
        files["image_file"] = (image_file.name, image_file.getvalue(), "image/jpeg")
    r = requests.post(f"{API_BASE}/query/multimodal", files=files, data=data)
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}


def get_health() -> dict:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        return r.json()
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}
