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

    API_BASE_URL = os.getenv("API_BASE_URL")