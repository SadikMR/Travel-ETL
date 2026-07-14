from flask import Flask

try:
    from .config import Config
    from .routes.booking import booking_bp
except ImportError:
    from config import Config
    from routes.booking import booking_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    app.register_blueprint(
        booking_bp,
        url_prefix="/api",
    )

    return app