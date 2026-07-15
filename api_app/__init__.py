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
        """Configure the Flask application and initialize extensions."""
        app.config.from_object(self.config)
        limiter.init_app(app)

    def register_blueprints(self, app: Flask) -> None:
        """Register all application blueprints."""

        from .routes.booking import booking_bp

        app.register_blueprint(booking_bp, url_prefix="/api")


def create_app() -> Flask:

    return ApiApp().create_app()