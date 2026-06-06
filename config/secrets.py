"""
config/secrets.py
-----------------
Fetches secrets from AWS Secrets Manager in prod/staging.
Falls back to environment variables in dev.
"""
from __future__ import annotations
import os
import json


def get_secret(secret_name: str, region: str = "ap-south-1") -> dict:
    """Fetch secret from AWS Secrets Manager."""
    import boto3
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def load_secrets() -> dict:
    """
    In prod/staging  → fetch from AWS Secrets Manager.
    In dev           → fall back to environment variables.
    """
    env = os.getenv("APP_ENV", "dev")

    if env in ("prod", "staging"):
        return get_secret("campus_chatbot/secrets")

    # dev — read from .env (already loaded by dotenv in settings.py)
    return {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
        "HUGGINGFACE_API_TOKEN": os.getenv("HUGGINGFACE_API_TOKEN", ""),
    }
