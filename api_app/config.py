import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    JSON_FILE = os.path.join(BASE_DIR, "data", "bookings.json")