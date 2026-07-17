from datetime import date
from decimal import Decimal
from typing import Any


BOOKINGS: list[dict[str, Any]] = [
    {
        "accommodations": {
            "reservation": "reservation-001",
        },
        "label": "k-us_d-mobile_p-10001",
        "accommodation_details": {
            "accommodation": "12345",
        },
        "status": "ok",
        "booker": {
            "travel_purpose": "business",
            "address": {
                "country": "bd",
            },
        },
        "currencies": {
            "booker": "EUR",
        },
        "start": "2026-07-10",
        "end": "2026-07-15",
        "commission": {
            "estimate_commission_amount": {
                "booker_currency": "100",
            },
        },
    }
]


NORMALIZED_COLUMNS: list[str] = [
    "accommodations.reservation",
    "label",
    "accommodation_details.accommodation",
    "status",
    "booker.travel_purpose",
    "booker.address.country",
    "currencies.booker",
    "start",
    "end",
    "commission.estimate_commission_amount.booker_currency",
]


PREPARED_RECORD: dict[str, Any] = {
    "transaction_id": "reservation-001",
    "conversion_key": "k-us_d-mobile_p-10001",
    "property_id": "12345",
    "status": "ok",
    "travel_purpose": "business",
    "country_code": "BD",
    "currency": "EUR",
    "check_in_date": date(2026, 7, 10),
    "check_out_date": date(2026, 7, 15),
    "revenue": 100,
}


TRANSFORMED_RECORD: dict[str, Any] = {
    "transaction_id": "reservation-001",
    "conversion_key": "k-us_d-mobile_p-10001",
    "property_id": "BC-12345",
    "status": "Confirmed",
    "travel_purpose": "business",
    "country_code": "BD",
    "currency": "USD",
    "check_in_date": date(2026, 7, 10),
    "check_out_date": date(2026, 7, 15),
    "revenue": Decimal("100.00"),
    "revenue_usd": Decimal("120.00"),
    "site_key": "US",
    "device": "Mobile",
    "referral_property_id": "10001",
}


CONVERSION_KEY: str = "k-us_d-mobile_p-10001"

SITE_KEY: str = "US"

DEVICE: str = "Mobile"

REFERRAL_PROPERTY_ID: str = "10001"

DECIMAL_VALUE: Decimal = Decimal("100.00")

USD_AMOUNT: Decimal = Decimal("120.00")