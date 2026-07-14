try:
    from . import create_app
    from .cronjobs.booking import run
except ImportError:
    from __init__ import create_app
    from cronjobs.booking import run

app = create_app()

with app.app_context():
    run()