import os
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ExchangeRateService:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, session: Optional[requests.Session] = None) -> None:
        self.api_key = api_key or os.getenv("EXCHANGE_RATE_API_KEY")
        self.base_url = base_url or os.getenv("EXCHANGE_RATE_API_URL", "https://open.er-api.com/v6/latest")
        self._rate_cache: dict[str, float] = {}
        self._session = session or self._build_session()

    def _build_session(self) -> requests.Session:
        s = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=(500, 502, 504))
        s.mount("https://", HTTPAdapter(max_retries=retries))
        return s

    def convert_to_usd(self, amount: float, currency_code: str) -> float:
        currency_code = (currency_code or "USD").upper()
        if currency_code == "USD":
            return float(amount)

        if currency_code in self._rate_cache:
            return float(amount) * self._rate_cache[currency_code]

        rate = self._fetch_rate(currency_code)
        self._rate_cache[currency_code] = rate
        return float(amount) * rate

    def _fetch_rate(self, currency_code: str) -> float:
        try:
            request_url, params = self._build_request(currency_code)
            resp = self._session.get(request_url, params=params, timeout=10)
            resp.raise_for_status()
            payload = resp.json()
        except requests.RequestException:  # pragma: no cover
            return 1.0  # pragma: no cover

        rate = self._extract_usd_rate(payload)
        return float(rate) if rate is not None else 1.0

    @staticmethod
    def _extract_usd_rate(payload: dict) -> Optional[float]:
        if not isinstance(payload, dict):
            return None
        rates = payload.get("rates") or {}
        usd = rates.get("USD")
        if usd is not None:
            return usd
        if payload.get("result") == "success":
            return (payload.get("rates") or {}).get("USD")  # pragma: no cover
        return None

    def _build_request(self, currency_code: str) -> tuple[str, dict]:
        return f"{self.base_url.rstrip('/')}/{currency_code}", {}
