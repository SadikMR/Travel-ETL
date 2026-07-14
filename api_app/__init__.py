from flask import Flask

from config import Config

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Limiter instance for decorators and global config
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
        # Parse RATELIMIT_DEFAULT which may be a semicolon-separated string or a list
        raw = getattr(self.config, "RATELIMIT_DEFAULT", None)
        default_limits = None
        if raw:
            if isinstance(raw, str):
                default_limits = [p.strip() for p in raw.split(";") if p.strip()]
            elif isinstance(raw, (list, tuple)):
                default_limits = list(raw)

        # Set config value so Flask-Limiter can pick up defaults on init_app
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

        # Register blueprint first, then apply per-endpoint limits on the app's
        # view functions so wrappers apply to the real endpoints.
        app.register_blueprint(booking_bp, url_prefix="/api")

        try:
            prefix = f"{booking_bp.name}."
            for ep, view in list(app.view_functions.items()):
                if ep.startswith(prefix):
                    app.view_functions[ep] = limiter.limit("10/minute")(view)
        except Exception:
            # non-fatal: skip per-endpoint wrapping if something goes wrong
            pass


def create_app() -> Flask:

    return ApiApp().create_app()