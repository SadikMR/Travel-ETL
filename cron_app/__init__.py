import sys
from pathlib import Path

CRON_APP_ROOT = Path(__file__).resolve().parent
if str(CRON_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(CRON_APP_ROOT))

from config import Config
from extensions import db


def create_app():
    db.initialize(uri=Config.SQLALCHEMY_DATABASE_URI)
    db.create_all()
    return db


def run_cron():
    from cronjobs.booking import run

    create_app()
    run()