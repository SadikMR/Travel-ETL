import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/travel_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Load API base URL from environment, fallback to local API used by dev
    _api_base = os.getenv("API_BASE_URL")
    if _api_base is None or str(_api_base).lower() == "none":
        _api_base = "http://127.0.0.1:5000"

    API_BASE_URL = _api_base