# Travel Booking ETL Pipeline

A Python-based ETL solution for processing travel booking data through two coordinated applications: a Flask REST API and a cron-driven ETL pipeline.

## Overview

This project is designed to:
- expose booking data through a lightweight API,
- extract booking records from a source endpoint,
- transform them into a normalized structure,
- and load them into PostgreSQL using SQLAlchemy.

The system is implemented with an object-oriented design following DRY and SOLID principles.

## Architecture

```text
+-------------------+       +----------------------+
|   Flask API       | ----> |   Booking Source    |
|   api_app/        |       |   (JSON / API)      |
+-------------------+       +----------+-----------+
          |                                |
          |                                v
          |                      +----------------------+
          |                      |   Cron ETL App      |
          |                      |   cron_app/         |
          |                      +----------+-----------+
          |                                 |
          +-------------------------------+------------------+
                                            |
                                            v
                                    +----------------------+
                                    |   PostgreSQL DB     |
                                    +----------------------+
```

## Features

- Flask REST API with booking retrieval endpoints
- Filtering support via `updated_from` and `updated_to`
- ETL flow with extract, transform, and load stages
- Currency conversion to USD using an exchange-rate service
- Booking status mapping and field normalization
- PostgreSQL UPSERT support to avoid duplicate inserts
- pandas-based transformation and batch processing
- Chunked loading with context-managed database sessions
- Pytest-based automated testing

## Technology Stack

| Layer | Technology |
| --- | --- |
| Language | Python |
| API | Flask |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| HTTP Client | requests |
| Data Processing | pandas |
| Testing | Pytest |
| Configuration | Dynaconf |

## Project Structure

```text
travel-etl/
├── api_app/
├── cron_app/
├── tests/
├── requirements.txt
├── settings.toml
├── docker-compose.yml
└── README.md
```

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

`.env` is optional, but the project will load it if present. It can be used to override values from `settings.toml` or provide secrets such as the exchange-rate API key.

Example:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=travel_etl
DB_USER=postgres
DB_PASSWORD=postgres
EXCHANGE_RATE_API_KEY=your_key_here
```

## Running the API

1. Activate the virtual environment:

```bash
source .venv/bin/activate
```

2. Install the Python dependencies:

```bash
pip install -r requirements.txt
```

3. Start the Flask API in one terminal:

```bash
python -m api_app.run
```

4. In a second terminal, start the required Docker services:

```bash
docker compose up -d
```

5. Access the API at:

```bash
http://127.0.0.1:5000/api/bookings
```

The API serves booking data under:

```text
GET /api/bookings
```

### Query Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `updated_from` | string | Start date in `YYYY-MM-DD` format |
| `updated_to` | string | End date in `YYYY-MM-DD` format |

## Running the ETL Application

1. Make sure the API is running and Docker services are up:

```bash
docker compose up -d
```

2. Run the booking ETL job from the project root:

```bash
python main.py --cron-name booking --updated_from 2026-07-12 --updated_to 2026-07-13
```

3. You can change the date values to any range you want.
4. This command executes the booking ETL workflow from `cron_app/cronjobs/booking.py` and loads the transformed data into PostgreSQL.

## API Endpoint Documentation

### GET /api/bookings
Returns booking records from the available source data.

Example:

```bash
curl "http://127.0.0.1:5000/api/bookings?updated_from=2026-07-01&updated_to=2026-07-31"
```

## ETL Workflow

The ETL process follows three stages:

1. Extract
   - Fetch booking data from the API or source data layer.

2. Transform
   - Rename source fields
   - Normalize booking data
   - Convert currency values to USD
   - Map booking statuses
   - Extract site, device, and referral properties from `conversion_key`

3. Load
   - Insert transformed records into PostgreSQL
   - Process rows in chunks for efficiency
   - Use context-managed database sessions for safe transaction handling
   - Use UPSERT logic to prevent duplicate rows

## Database Schema Overview

The loading layer uses SQLAlchemy models to represent booking-related data in PostgreSQL. Records are stored with normalized columns suitable for downstream analysis and reporting, and the load step uses chunked writes with managed sessions for reliability.

## Testing

Run the test suite with:

```bash
pytest
```

## Design Principles

This project follows:
- **OOP** for clear separation of responsibilities across services and models
- **SOLID** for maintainable and extensible class design
- **DRY** to reduce duplication and improve consistency

## Error Handling

The application handles common failures gracefully by:
- validating input parameters,
- catching request and database errors,
- logging relevant issues,
- and avoiding duplicate inserts during load.

## Assumptions

- The source booking data is available through the configured API or JSON input.
- PostgreSQL is available and accessible with the provided credentials.
- Date filters are provided in `YYYY-MM-DD` format.

## Future Improvements

- Add authentication and authorization for the API
- Support additional cron jobs and ETL sources
- Introduce container-based deployment improvements
- Add monitoring and metrics for ETL execution


