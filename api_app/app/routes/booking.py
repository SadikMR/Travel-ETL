import json
from datetime import date, datetime

from flask import Blueprint, current_app, jsonify, request

booking_bp = Blueprint("booking", __name__)


@booking_bp.get("/bookings")
def get_bookings():
    updated_from = request.args.get("updated_from")
    updated_to = request.args.get("updated_to")

    with open(current_app.config["JSON_FILE"], "r", encoding="utf-8") as file:
        bookings = json.load(file)

    if not updated_from and not updated_to:
        return jsonify(bookings)

    if updated_from:
        updated_from = date.fromisoformat(updated_from)

    if updated_to:
        updated_to = date.fromisoformat(updated_to)

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