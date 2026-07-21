import sys
from pathlib import Path

import sentry_sdk

CRON_APP_ROOT = Path(__file__).resolve().parent
if str(CRON_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(CRON_APP_ROOT))

from config import Config
from extensions import db


def initialize_sentry() -> None:
    """Initialize Sentry for the cron application."""
    if Config.SENTRY_DSN:
        sentry_sdk.init(
            dsn=Config.SENTRY_DSN,
            environment=Config.SENTRY_ENVIRONMENT,
            traces_sample_rate=Config.SENTRY_TRACES_SAMPLE_RATE,
            send_default_pii=True,
        )
    else:
        print("Warning: Sentry DSN not configured. Exception tracking will be disabled.")  # pragma: no cover


def create_app():
    initialize_sentry()
    db.initialize(uri=Config.SQLALCHEMY_DATABASE_URI)
    db.create_all()
    return db


def run_cron():
    from cronjobs.booking import run

    create_app()
    run()