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
        
        # Initialize Sentry with proper configuration
        if self.config.SENTRY_DSN:
            sentry_sdk.init(
                dsn=self.config.SENTRY_DSN,
                environment=self.config.SENTRY_ENVIRONMENT,
                traces_sample_rate=self.config.SENTRY_TRACES_SAMPLE_RATE,
                # Add data like request headers and IP for users,
                # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
                send_default_pii=True,
            )
        else:
            # Sentry is optional - log a warning if DSN is not configured
            app.logger.warning("Sentry DSN not configured. Exception tracking will be disabled.")

        limiter.init_app(app)

    def register_blueprints(self, app: Flask) -> None:
        from .routes.booking import booking_bp

        app.register_blueprint(booking_bp, url_prefix="/api")


def create_app() -> Flask:
    return ApiApp().create_app()