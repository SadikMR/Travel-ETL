import requests

from config import Config
from services.booking_extract_service import BookingExtractService
from services.booking_load_service import BookingLoadService
from services.booking_transform_service import BookingTransformService
from services.exchange_rate_service import ExchangeRateService


class BookingCron:

    def __init__(self) -> None:
        self.extract_service = BookingExtractService()
        self.transform_service = BookingTransformService(
            exchange_rate_service=ExchangeRateService()
        )
        self.load_service = BookingLoadService()

    def get_query_params(self) -> dict:
        return {
            "updated_from": "2026-07-13",
            "updated_to": "2026-07-13",
        }

    def fetch_bookings(self) -> list[dict]:
        return self.extract_service.fetch(self.get_query_params())

    def transform_bookings(self, bookings: list[dict]) -> list[dict]:
        return self.transform_service.transform(bookings)

    def load_bookings(self, bookings: list[dict]) -> int:
        return self.load_service.load(bookings)

    def run(self) -> None:
        try:
            bookings = self.fetch_bookings()
            print(f"Fetched {len(bookings)} bookings.")

            transformed = self.transform_bookings(bookings)
            print(f"Transformed {len(transformed)} bookings.")

            inserted = self.load_bookings(transformed)
            print(f"Inserted {inserted} new bookings.")

        except requests.RequestException as error:
            print(f"API request failed: {error}")


def run() -> None:
    """Module-level compatibility function used by the runner."""

    BookingCron().run()