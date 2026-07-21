import os
from pathlib import Path

from dynaconf import Dynaconf

BASE_DIR = Path(__file__).resolve().parent

settings = Dynaconf(
    settings_files=[
        str(Path(BASE_DIR).parents[0] / "settings.toml"),
    ]
)


class Config:
    JSON_FILE = settings.get("JSON_FILE") or str(BASE_DIR / "data" / "bookings.json")
    RATELIMIT_DEFAULT = settings.get("RATELIMIT_DEFAULT") or "100/hour;1000/day"

    # Sentry: DSN from environment variable (set via docker env_file or .env)
    SENTRY_DSN = os.getenv("SENTRY_DSN") or settings.get("SENTRY_DSN")
    SENTRY_ENVIRONMENT = settings.get("SENTRY_ENVIRONMENT") or "development"
    SENTRY_TRACES_SAMPLE_RATE = float(settings.get("SENTRY_TRACES_SAMPLE_RATE") or 1.0)