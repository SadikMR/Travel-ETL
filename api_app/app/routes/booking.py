import json
from datetime import date, datetime

from flask import Blueprint, current_app, jsonify, request

booking_bp = Blueprint("booking", __name__)


@booking_bp.get("/bookings")
def get_bookings():
    updated_from = request.args.get("updated_from")
    updated_to = request.args.get("updated_to")

    # Validate date format
    try:
        if updated_from:
            updated_from = date.fromisoformat(updated_from)

        if updated_to:
            updated_to = date.fromisoformat(updated_to)

    except ValueError:
        return (
            jsonify(
                {
                    "message": "Dates must be in YYYY-MM-DD format."
                }
            ),
            400,
        )

    # Validate date range
    if updated_from and updated_to and updated_from > updated_to:
        return (
            jsonify(
                {
                    "message": "updated_from cannot be later than updated_to."
                }
            ),
            400,
        )

    # Read JSON file
    try:
        with open(current_app.config["JSON_FILE"], "r", encoding="utf-8") as file:
            bookings = json.load(file)

    except FileNotFoundError:
        return (
            jsonify(
                {
                    "message": "Bookings data file not found."
                }
            ),
            404,
        )

    except json.JSONDecodeError:
        return (
            jsonify(
                {
                    "message": "Bookings data file is not a valid JSON."
                }
            ),
            500,
        )

    # No filters provided
    if not updated_from and not updated_to:
        return jsonify(bookings)

    filtered_bookings = []

    for booking in bookings:
        booking_date = datetime.fromisoformat(
            booking["updated"].replace("Z", "+00:00")
        ).date()

        if updated_from and booking_date < updated_from:
            continue

        if updated_to and booking_date > updated_to:
            continue

        filtered_bookings.append(booking)

    return jsonify(filtered_bookings)