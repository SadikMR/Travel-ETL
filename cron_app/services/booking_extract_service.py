import requests
from typing import Optional

from config import Config


class BookingExtractService:
    DEFAULT_ENDPOINT = "/api/bookings"

    def __init__(self, base_url: Optional[str] = None, endpoint: Optional[str] = None) -> None:
        self.base_url = base_url or Config.API_BASE_URL
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT

    def _build_url(self) -> str:
        return f"{str(self.base_url).rstrip('/')}{self.endpoint}"

    def _request(self, params: dict) -> requests.Response:
        url = self._build_url()
        return requests.get(url=url, params=params, timeout=30)

    def fetch(self, params: dict) -> list:
        """Fetch bookings using configured base URL and query params."""

        response = self._request(params)
        response.raise_for_status()
        return response.json()