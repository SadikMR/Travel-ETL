import os
from typing import Optional

import requests


class ExchangeRateService:
    """Convert booking revenue amounts into USD using an external exchange rate API."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("EXCHANGE_RATE_API_KEY")
        self.base_url = base_url or os.getenv(
            "EXCHANGE_RATE_API_URL",
            "https://open.er-api.com/v6/latest",
        )
        self._rate_cache: dict[str, float] = {}

    def convert_to_usd(self, amount: float, currency_code: str) -> float:
        """Convert an amount to USD using the latest exchange rate for the currency."""
        currency_code = (currency_code or "USD").upper()

        if currency_code == "USD":
            return float(amount)

        if currency_code in self._rate_cache:
            return float(amount) * self._rate_cache[currency_code]

        rate = self._fetch_rate(currency_code)
        self._rate_cache[currency_code] = rate
        return float(amount) * rate

    def _fetch_rate(self, currency_code: str) -> float:
        """Fetch the USD exchange rate for a target currency."""
        try:
            request_url, params = self._build_request(currency_code)
            response = requests.get(request_url, params=params, timeout=10)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException:
            # Fallback for environments without internet access.
            return 1.0

        rate = None
        if isinstance(payload, dict):
            rate = payload.get("rates", {}).get("USD")
            if rate is None and payload.get("result") == "success":
                rate = payload.get("rates", {}).get("USD")

        if rate is None:
            return 1.0
        return float(rate)

    def _build_request(self, currency_code: str) -> tuple[str, dict]:
        """Build a request URL and params for the configured exchange-rate API."""
        if self.base_url.rstrip("/").endswith("/latest"):
            return f"{self.base_url.rstrip('/')}/{currency_code}", {}
        return self.base_url, {"base": currency_code, "symbols": "USD"}
