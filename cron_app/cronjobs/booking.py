import requests
import sentry_sdk

from config import Config
from services.booking_extract_service import BookingExtractService
from services.booking_load_service import BookingLoadService
from services.booking_transform_service import BookingTransformService
from services.exchange_rate_service import ExchangeRateService


class BookingCron:

    def __init__(self, updated_from: str | None = None, updated_to: str | None = None) -> None:
        self.updated_from = updated_from
        self.updated_to = updated_to
        self.extract_service = BookingExtractService()
        self.transform_service = BookingTransformService(
            exchange_rate_service=ExchangeRateService()
        )
        self.load_service = BookingLoadService()

    def get_query_params(self) -> dict:
        if not self.updated_from or not self.updated_to:
            raise ValueError("Both 'updated_from' and 'updated_to' must be provided.") 
        
        return {
            "updated_from": self.updated_from,
            "updated_to": self.updated_to,
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

            if bookings is None:
                error_msg = "No booking data received from API: response was empty or null."
                print(error_msg)
                return

            if not isinstance(bookings, list):
                error_msg = "No booking data received from API: response was not a list."
                print(error_msg)
                return

            if not bookings:
                error_msg = "No booking data received from API: response was empty."
                print(error_msg)
                return

            print(f"Fetched {len(bookings)} bookings.")

            transformed = self.transform_bookings(bookings)
            print(f"Transformed {len(transformed)} bookings.")

            inserted = self.load_bookings(transformed)
            print(f"Inserted {inserted} new bookings.")

        except ValueError as error:  # pragma: no cover
            error_msg = f"Validation error in booking cron: {error}"  # pragma: no cover
            print(error_msg)  # pragma: no cover
            sentry_sdk.capture_exception(error)  # pragma: no cover
            sentry_sdk.capture_message(error_msg, level="warning")  # pragma: no cover
            
        except requests.RequestException as error:  # pragma: no cover
            error_msg = f"API request failed: {error}"  # pragma: no cover
            print(error_msg)  # pragma: no cover
            sentry_sdk.capture_exception(error)  # pragma: no cover
            sentry_sdk.capture_message(error_msg, level="error")  # pragma: no cover
            
        except Exception as error:  # pragma: no cover
            error_msg = f"Unexpected error in booking cron job: {error}"  # pragma: no cover
            print(error_msg)  # pragma: no cover
            sentry_sdk.capture_exception(error)  # pragma: no cover
            sentry_sdk.capture_message(error_msg, level="error")  # pragma: no cover


def run(updated_from: str | None = None, updated_to: str | None = None) -> None:

    BookingCron(updated_from=updated_from, updated_to=updated_to).run()