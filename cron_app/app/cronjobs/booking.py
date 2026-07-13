import requests

from app.config import Config
from app.services.booking_service import BookingService


def get_api_url() -> str:
    return f"{Config.API_BASE_URL}/api/bookings"


def get_query_params() -> dict:
    return {
        "updated_from": "2026-07-13",
        "updated_to": "2026-07-13",
    }


def fetch_bookings():
    service = BookingService()

    api_url = get_api_url()
    params = get_query_params()

    return service.fetch(api_url, params)


def run():
    try:
        bookings = fetch_bookings()

        print(f"Fetched {len(bookings)} bookings")

        return bookings

    except requests.RequestException as e:
        print(f"API request failed: {e}")