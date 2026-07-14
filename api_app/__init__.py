from flask import Flask

from config import Config

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


class ApiApp:

    def __init__(self, config: type[Config] = Config) -> None:
        self.config = config

    def create_app(self) -> Flask:
        app = Flask(__name__)
        self.configure_app(app)
        self.register_blueprints(app)
        return app

    def configure_app(self, app: Flask) -> None:
        """Apply configuration to the Flask app."""

        app.config.from_object(self.config)
        raw = getattr(self.config, "RATELIMIT_DEFAULT", None)
        default_limits = None
        if raw:
            if isinstance(raw, str):
                default_limits = [p.strip() for p in raw.split(";") if p.strip()]
            elif isinstance(raw, (list, tuple)):
                default_limits = list(raw)

        if default_limits is not None:
            # Flask-Limiter expects a string like "10/minute;1000/day" in config
            if isinstance(getattr(self.config, "RATELIMIT_DEFAULT", None), str):
                app.config["RATELIMIT_DEFAULT"] = getattr(self.config, "RATELIMIT_DEFAULT")
            else:
                app.config["RATELIMIT_DEFAULT"] = ";".join(default_limits)

        # Initialize limiter from app config (reads RATELIMIT_DEFAULT)
        limiter.init_app(app)

    def register_blueprints(self, app: Flask) -> None:
        """Register all application blueprints."""

        from routes.booking import booking_bp


        app.register_blueprint(booking_bp, url_prefix="/api")

        try:
            prefix = f"{booking_bp.name}."
            for ep, view in list(app.view_functions.items()):
                if ep.startswith(prefix):
                    app.view_functions[ep] = limiter.limit("10/minute")(view)
        except Exception:
            pass


def create_app() -> Flask:

    return ApiApp().create_app()