import json
from datetime import date, datetime
from typing import Optional

import sentry_sdk
from flask import Blueprint, current_app, jsonify, request
from flask.views import MethodView

from ..extensions import limiter

booking_bp = Blueprint("booking", __name__)


class BookingAPI(MethodView):

    def get(self):
        updated_from_str = request.args.get("updated_from")
        updated_to_str = request.args.get("updated_to")

        try:
            updated_from, updated_to = self._parse_dates(
                updated_from_str, updated_to_str
            )
        except ValueError as e:
            error_msg = "Dates must be in YYYY-MM-DD format."
            sentry_sdk.capture_exception(e)  # pragma: no cover
            sentry_sdk.capture_message("Date parsing failed", level="warning")  # pragma: no cover
            return jsonify({"message": error_msg}), 400

        if updated_from and updated_to and updated_from > updated_to:
            error_msg = "updated_from cannot be later than updated_to."
            sentry_sdk.capture_message(error_msg, level="warning")  # pragma: no cover
            return (
                jsonify({"message": error_msg}),
                400,
            )

        try:
            bookings = self._load_bookings()
        except FileNotFoundError as e:
            error_msg = "Bookings data file not found."
            sentry_sdk.capture_exception(e)  # pragma: no cover
            sentry_sdk.capture_message(error_msg, level="error")  # pragma: no cover
            return jsonify({"message": error_msg}), 404
        except json.JSONDecodeError as e:
            error_msg = "Bookings data file is not a valid JSON."
            sentry_sdk.capture_exception(e)  # pragma: no cover
            sentry_sdk.capture_message(error_msg, level="error")  # pragma: no cover
            return jsonify({"message": error_msg}), 500

        if not updated_from and not updated_to:
            return jsonify(bookings)

        filtered = self._filter_bookings(bookings, updated_from, updated_to)
        return jsonify(filtered)

    def _parse_dates(self, updated_from: Optional[str], updated_to: Optional[str]):
        """Parse optional date strings into date objects or None."""

        uf = date.fromisoformat(updated_from) if updated_from else None
        ut = date.fromisoformat(updated_to) if updated_to else None
        return uf, ut

    def _load_bookings(self):
        """Read bookings JSON from configured path."""

        with open(current_app.config["JSON_FILE"], "r", encoding="utf-8") as fh:
            return json.load(fh)

    def _filter_bookings(self, bookings: list[dict], updated_from: Optional[date], updated_to: Optional[date]) -> list[dict]:
        """Return bookings within optional date range."""

        out: list[dict] = []
        for booking in bookings:
            booking_date = datetime.fromisoformat(
                booking["updated"].replace("Z", "+00:00")
            ).date()

            if updated_from and booking_date < updated_from:
                continue

            if updated_to and booking_date > updated_to:
                continue

            out.append(booking)

        return out
    

class SentryTestAPI(MethodView):
    """Endpoint to verify Sentry integration."""

    def get(self):
        try:
            raise Exception("Test exception for Sentry verification")
        except Exception as e:
            sentry_sdk.capture_exception(e)  # pragma: no cover
            sentry_sdk.capture_message("Sentry test exception captured", level="warning")  # pragma: no cover
            return jsonify({"message": "Test exception sent to Sentry"}), 200
    

booking_view = BookingAPI.as_view("booking_api")
booking_view = limiter.limit("10/minute")(booking_view)
booking_bp.add_url_rule("/bookings", view_func=booking_view, methods=["GET"])

sentry_test_view = SentryTestAPI.as_view("sentry_test_api")
sentry_test_view = limiter.limit("5/minute")(sentry_test_view)
booking_bp.add_url_rule("/sentry-test", view_func=sentry_test_view, methods=["GET"])
