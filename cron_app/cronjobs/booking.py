import requests

from config import Config
from services.booking_extract_service import (
    BookingExtractService,
)
from services.booking_load_service import (
    BookingLoadService,
)
from services.booking_transform_service import (
    BookingTransformService,
)
from services.exchange_rate_service import ExchangeRateService


def get_api_url() -> str:
    """Return bookings API endpoint."""

    return f"{Config.API_BASE_URL}/api/bookings"


def get_query_params() -> dict:
    """Return query parameters for the bookings API."""

    return {
        "updated_from": "2026-07-13",
        "updated_to": "2026-07-13",
    }


def run():
    """Run the booking ETL pipeline."""

    extract_service = BookingExtractService()
    transform_service = BookingTransformService(
        exchange_rate_service=ExchangeRateService()
    )
    load_service = BookingLoadService()

    try:
        bookings = extract_service.fetch(
            url=get_api_url(),
            params=get_query_params(),
        )

        print(f"Fetched {len(bookings)} bookings.")

        transformed_bookings = transform_service.transform(
            bookings
        )

        print(
            f"Transformed {len(transformed_bookings)} bookings."
        )

        inserted_count = load_service.load(
            transformed_bookings
        )

        print(
            f"Inserted {inserted_count} new bookings."
        )

    except requests.RequestException as error:
        print(f"API request failed: {error}")