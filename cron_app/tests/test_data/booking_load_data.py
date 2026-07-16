from datetime import date
from decimal import Decimal

BOOKING_1 = {
    "transaction_id": "TXN001",
    "conversion_key": "k-us_d-mobile_p-10001",
    "property_id": "BC-10001",
    "status": "Confirmed",
    "travel_purpose": "Leisure",
    "country_code": "US",
    "currency": "USD",
    "check_in_date": date(2026, 7, 1),
    "check_out_date": date(2026, 7, 5),
    "site_key": "US",
    "device": "Mobile",
    "referral_property_id": "10001",
    "revenue": Decimal("100.00"),
    "revenue_usd": Decimal("100.00"),
}

BOOKING_2 = {
    "transaction_id": "TXN002",
    "conversion_key": "k-uk_d-desktop_p-10002",
    "property_id": "BC-10002",
    "status": "Cancelled",
    "travel_purpose": "Business",
    "country_code": "GB",
    "currency": "GBP",
    "check_in_date": date(2026, 8, 1),
    "check_out_date": date(2026, 8, 3),
    "site_key": "UK",
    "device": "Desktop",
    "referral_property_id": "10002",
    "revenue": Decimal("200.00"),
    "revenue_usd": Decimal("250.00"),
}

BOOKINGS = [
    BOOKING_1,
    BOOKING_2,
]

EMPTY_BOOKINGS = []

EXISTING_TRANSACTION_IDS = {
    BOOKING_1["transaction_id"],
}

ALL_TRANSACTION_IDS = [
    BOOKING_1["transaction_id"],
    BOOKING_2["transaction_id"],
]

NEW_COUNT = 1
UPDATED_COUNT = 1