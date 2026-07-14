import json
import re
from pathlib import Path
from typing import Optional

import pandas as pd

from services.exchange_rate_service import ExchangeRateService


class BookingTransformService:
    PROPERTY_PREFIX = "BC"
    SOURCE_COLUMNS = [
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

    RENAME_MAP = {
        "accommodations.reservation": "transaction_id",
        "label": "conversion_key",
        "accommodation_details.accommodation": "property_id",
        "booker.travel_purpose": "travel_purpose",
        "booker.address.country": "country_code",
        "currencies.booker": "currency",
        "start": "check_in_date",
        "end": "check_out_date",
        "commission.estimate_commission_amount.booker_currency": "revenue",
    }

    _SITE_RE = re.compile(r"k-([^_]+)")
    _DEVICE_RE = re.compile(r"d-([^_]+)")
    _REFERRAL_RE = re.compile(r"p-([^_]+)")

    def __init__(self, exchange_rate_service: Optional[ExchangeRateService] = None) -> None:
        self._status_mapping = self._load_mapping("booking_status.json")
        self._device_mapping = self._load_mapping("device_mapping.json")
        self._exchange_rate_service = exchange_rate_service or ExchangeRateService()

    def transform(self, bookings: list[dict]) -> list[dict]:
        df = self._normalize(bookings)
        df = self._prepare_dataframe(df)
        return [self._transform_record(r) for r in df.to_dict(orient="records")]

    def _normalize(self, bookings: list[dict]) -> pd.DataFrame:
        return pd.json_normalize(bookings)

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[self.SOURCE_COLUMNS].copy()
        df.rename(columns=self.RENAME_MAP, inplace=True)
        self._convert_date_columns(df, ["check_in_date", "check_out_date"])
        df["country_code"] = df["country_code"].fillna("").str.upper()
        df["revenue"] = df["revenue"].fillna(0)
        return df

    @staticmethod
    def _convert_date_columns(df: pd.DataFrame, cols: list[str]) -> None:
        for c in cols:
            df[c] = pd.to_datetime(df[c]).dt.date

    def _transform_record(self, record: dict) -> dict:
        record["property_id"] = f"{self.PROPERTY_PREFIX}-{record["property_id"]}"
        record["status"] = self._status_mapping.get(record.get("status"), record.get("status"))

        conversion_key = record.get("conversion_key") or ""
        record["site_key"] = self._extract_site_key(conversion_key)
        record["device"] = self._extract_device(conversion_key)
        record["referral_property_id"] = self._extract_referral_property_id(conversion_key)

        currency = record.get("currency") or "USD"
        revenue = record.get("revenue") or 0
        record["revenue"] = self._exchange_rate_service.convert_to_usd(revenue, currency)
        record["currency"] = "USD"
        return record

    def _extract_site_key(self, conversion_key: str) -> Optional[str]:
        m = self._SITE_RE.search(conversion_key)
        return m.group(1).upper() if m else None

    def _extract_device(self, conversion_key: str) -> Optional[str]:
        m = self._DEVICE_RE.search(conversion_key)
        return self._device_mapping.get(m.group(1)) if m else None

    def _extract_referral_property_id(self, conversion_key: str) -> Optional[str]:
        m = self._REFERRAL_RE.search(conversion_key)
        return m.group(1) if m else None

    @staticmethod
    def _load_mapping(filename: str) -> dict:
        mapping_path = Path(__file__).resolve().parents[1] / "mappings" / filename
        with open(mapping_path, "r", encoding="utf-8") as fh:
            return json.load(fh)