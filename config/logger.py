"""
config/logger.py
----------------
Dev      → human readable → console + logs/dev/app.log
Staging  → JSON           → console + logs/staging/app.log
Prod     → JSON           → console + logs/prod/app.log
errors always → logs/{env}/error.log
"""
from __future__ import annotations
import logging
import logging.handlers
import json
import os
from pathlib import Path
from datetime import datetime, timezone

# ── Log directory ─────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
APP_ENV  = os.getenv("APP_ENV", "dev")
LOG_DIR  = BASE_DIR / "logs" / APP_ENV
LOG_DIR.mkdir(parents=True, exist_ok=True)


class JsonFormatter(logging.Formatter):
    """Formats log records as JSON for staging/prod."""
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level":     record.levelname,
            "logger":    record.name,
            "message":   record.getMessage(),
            "module":    record.module,
            "function":  record.funcName,
        })


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG if APP_ENV == "dev" else logging.INFO)

    # ── Formatters ────────────────────────────────────────────────────────
    if APP_ENV in ("prod", "staging"):
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # ── Console handler ───────────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # ── app.log — all levels, rotates at 5MB, keeps 5 backups ────────────
    app_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(logging.DEBUG)

    # ── error.log — errors only, rotates at 2MB, keeps 5 backups ─────────
    error_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "error.log",
        maxBytes=2 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    logger.addHandler(console_handler)
    logger.addHandler(app_handler)
    logger.addHandler(error_handler)
    logger.propagate = False
    return logger