import os
from pathlib import Path
from dynaconf import Dynaconf

BASE_DIR = Path(__file__).resolve().parents[1]

settings = Dynaconf(
    settings_files=[str(BASE_DIR / "settings.toml")],
)


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI") or settings.get(
        "DATABASE_URI",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/travel_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_BASE_URL = settings.get("API_BASE_URL", "http://127.0.0.1:5000")

    # Sentry: DSN from environment variable (set via docker env_file or .env)
    SENTRY_DSN = os.getenv("SENTRY_DSN") or settings.get("SENTRY_DSN")
    SENTRY_ENVIRONMENT = settings.get("SENTRY_ENVIRONMENT") or "development"
    SENTRY_TRACES_SAMPLE_RATE = float(settings.get("SENTRY_TRACES_SAMPLE_RATE") or 1.0)