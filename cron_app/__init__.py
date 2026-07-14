from flask import Flask

try:
    from .config import Config
    from .extensions import db
except ImportError:
    from config import Config
    from extensions import db


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from models import BookingTransaction

        db.create_all()

    return app