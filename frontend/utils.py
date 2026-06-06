import requests
import time

API_BASE = "http://127.0.0.1:8000"

def call_text(query: str) -> dict:
    t0 = time.perf_counter()
    r  = requests.post(f"{API_BASE}/query/text", json={"query": query})
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}

def call_audio(audio_path: str) -> dict:
    t0 = time.perf_counter()
    r  = requests.post(f"{API_BASE}/query/audio", json={"audio_path": audio_path})
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}

def call_image(image_path: str) -> dict:
    t0 = time.perf_counter()
    r  = requests.post(f"{API_BASE}/query/image", json={"image_path": image_path})
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}

def call_audio_text(audio_path: str, text_query: str = None) -> dict:
    t0 = time.perf_counter()
    r  = requests.post(f"{API_BASE}/query/audio-text", json={
        "query": audio_path, "text_query": text_query
    })
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}

def call_multimodal(query: str = None, audio_path: str = None, image_path: str = None) -> dict:
    t0 = time.perf_counter()
    r  = requests.post(f"{API_BASE}/query/multimodal", json={
        "query": query, "audio_path": audio_path, "image_path": image_path
    })
    return {**r.json(), "latency": round(time.perf_counter() - t0, 3)}

def get_health() -> dict:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        return r.json()
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}