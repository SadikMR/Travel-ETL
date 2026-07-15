from pathlib import Path
from dynaconf import Dynaconf

BASE_DIR = Path(__file__).resolve().parents[1]

settings = Dynaconf(
    environments=True,
    settings_files=[str(BASE_DIR / "settings.toml"), str(BASE_DIR / ".secrets.toml"), str(BASE_DIR / ".env")],
)


class Config:
    SQLALCHEMY_DATABASE_URI = settings.get(
        "DATABASE_URI",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/travel_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_BASE_URL = settings.get("API_BASE_URL", "http://127.0.0.1:5000")