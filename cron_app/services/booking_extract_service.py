import requests


class BookingExtractService:
    """Handles communication with the API."""

    def fetch(self, url: str, params: dict) -> list:
        response = requests.get(
            url=url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()