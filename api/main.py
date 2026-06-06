import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from config.settings import validate
from config.logger import get_logger
from api.routes import text, audio, image, audio_text, multimodal
from core.model_loader import health_check as model_health_check
import os

validate()


import asyncio

# ── Semaphores for heavy model endpoints ──────────────────────────────────
whisper_semaphore = asyncio.Semaphore(2)
clip_semaphore    = asyncio.Semaphore(2)

logger = get_logger(__name__)
app    = FastAPI(
    title       = "Campus Chatbot API",
    description = "Multimodal campus navigation chatbot",
    version     = "1.0.0",
)

# ── Latency tracking middleware ───────────────────────────────────────────
@app.middleware("http")
async def latency_middleware(request: Request, call_next):
    t0       = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - t0
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)")
    return response

# ── Register routes ───────────────────────────────────────────────────────
app.include_router(text.router)
app.include_router(audio.router)
app.include_router(image.router)
app.include_router(audio_text.router)
app.include_router(multimodal.router)

# ── Global error handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code = 500,
        content     = {"answer": "", "pipeline": "unknown", "error": str(exc)},
    )

# ── Health check ──────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    model_status = model_health_check()
    return {
        "status": model_status["status"],
        "models": model_status,
        "env":    os.getenv("APP_ENV", "dev"),
    }