from app import create_app
from app.cronjobs.booking import run

app = create_app()

with app.app_context():
    run()