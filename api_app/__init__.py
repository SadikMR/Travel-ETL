import sentry_sdk
from flask import Flask

from .config import Config
from .extensions import limiter


class ApiApp:

    def __init__(self, config: type[Config] = Config) -> None:
        self.config = config

    def create_app(self) -> Flask:
        app = Flask(__name__)
        self.configure_app(app)
        self.register_blueprints(app)
        return app

    def configure_app(self, app: Flask) -> None:
        app.config.from_object(self.config)
        sentry_sdk.init(
            dsn="https://0b21e6deba31d0b186c0990113a409b9@o4511771590459392.ingest.us.sentry.io/4511771617656832",
            # Add data like request headers and IP for users,
            # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
            send_default_pii=True,
        )
        sentry_sdk.capture_message("Travel ETL startup")

        limiter.init_app(app)

    def register_blueprints(self, app: Flask) -> None:
        from .routes.booking import booking_bp

        app.register_blueprint(booking_bp, url_prefix="/api")


def create_app() -> Flask:
    return ApiApp().create_app()