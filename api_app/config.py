from pathlib import Path
from dynaconf import Dynaconf

BASE_DIR = Path(__file__).resolve().parent

settings = Dynaconf(settings_files=[str(Path(BASE_DIR).parents[0] / "settings.toml"), str(Path(BASE_DIR).parents[0] / ".env")])


class Config:
    JSON_FILE = settings.get("JSON_FILE") or str(BASE_DIR / "data" / "bookings.json")
    RATELIMIT_DEFAULT = settings.get("RATELIMIT_DEFAULT") or "100/hour;1000/day"