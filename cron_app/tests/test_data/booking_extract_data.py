BASE_URL = "http://localhost:5000"

ENDPOINT = "/api/bookings"

URL = f"{BASE_URL}{ENDPOINT}"

REQUEST_TIMEOUT = 30

VALID_PARAMS = {
    "updated_from": "2026-07-10",
    "updated_to": "2026-07-12",
}

SUCCESS_RESPONSE = [
    {"id": "1"},
    {"id": "2"},
]

HTTP_ERROR_MESSAGE = "404 Not Found"