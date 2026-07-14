import json
from datetime import date, datetime
from typing import Optional

from flask import Blueprint, current_app, jsonify, request
from flask.views import MethodView

booking_bp = Blueprint("booking", __name__)


class BookingAPI(MethodView):

    def get(self):
        updated_from_str = request.args.get("updated_from")
        updated_to_str = request.args.get("updated_to")

        try:
            updated_from, updated_to = self._parse_dates(
                updated_from_str, updated_to_str
            )
        except ValueError:
            return jsonify({"message": "Dates must be in YYYY-MM-DD format."}), 400

        if updated_from and updated_to and updated_from > updated_to:
            return (
                jsonify({"message": "updated_from cannot be later than updated_to."}),
                400,
            )

        try:
            bookings = self._load_bookings()
        except FileNotFoundError:
            return jsonify({"message": "Bookings data file not found."}), 404
        except json.JSONDecodeError:
            return jsonify({"message": "Bookings data file is not a valid JSON."}), 500

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


booking_view = BookingAPI.as_view("booking_api")
booking_bp.add_url_rule("/bookings", view_func=booking_view, methods=["GET"]) 