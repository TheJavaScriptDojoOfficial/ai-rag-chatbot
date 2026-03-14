"""
Minimal config using environment variables.
Ready for future CORS and app settings.
"""
import os


def get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# CORS: allowed origins (comma-separated in env, or default for local dev)
CORS_ORIGINS_RAW = get_env("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_RAW.split(",") if origin.strip()]
