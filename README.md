# travel-etl

A simple ETL project with a Flask API and cron-based booking processing.

## Installation

1. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run the API

From the project root, start the Flask API with:
```bash
python -m api_app.run
```

The API is configured in `api_app/__init__.py` and exposes routes under `/api`.

## Run a cron job

From the project root, use `main.py` to execute cron modules by name.

Example:
```bash
python main.py --cron-name booking --updated_from 2026-07-12 --updated_to 2026-07-13
```

### Notes

- `--cron-name` can be specified multiple times to run more than one cron job.
- `--updated_from` and `--updated_to` are optional date filters in `YYYY-MM-DD` format.
- The root entrypoint for cron jobs is `main.py`, which imports cron modules from `cron_app/cronjobs`.

