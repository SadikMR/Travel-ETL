import json
import re
from pathlib import Path

import pandas as pd

try:
    from .exchange_rate_service import ExchangeRateService
except ImportError:
    from services.exchange_rate_service import ExchangeRateService


class BookingTransformService:
    """Transforms raw booking data into database-ready records."""

    PROPERTY_PREFIX = "BC"

    def __init__(self, exchange_rate_service: ExchangeRateService | None = None) -> None:
        self._status_mapping = self._load_mapping(
            "booking_status.json"
        )

        self._device_mapping = self._load_mapping(
            "device_mapping.json"
        )
        self._exchange_rate_service = (
            exchange_rate_service or ExchangeRateService()
        )

    def transform( self, bookings: list[dict]) -> list[dict]:
        """Transform raw booking JSON into database-ready records."""

        dataframe = self._normalize(bookings)
        dataframe = self._prepare_dataframe(dataframe)

        records = dataframe.to_dict(orient="records")

        return [
            self._transform_record(record)
            for record in records
        ]

    def _normalize(self,bookings: list[dict]) -> pd.DataFrame:
        """Flatten nested booking JSON."""

        return pd.json_normalize(bookings)

    def _prepare_dataframe(self,dataframe: pd.DataFrame) -> pd.DataFrame:
        """Prepare dataframe using Pandas transformations."""

        dataframe = dataframe[
            [
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
        ].copy()

        dataframe.rename(
            columns={
                "accommodations.reservation": "transaction_id",
                "label": "conversion_key",
                "accommodation_details.accommodation": "property_id",
                "booker.travel_purpose": "travel_purpose",
                "booker.address.country": "country_code",
                "currencies.booker": "currency",
                "start": "check_in_date",
                "end": "check_out_date",
                "commission.estimate_commission_amount.booker_currency": "revenue",
            },
            inplace=True,
        )

        dataframe["check_in_date"] = (
            pd.to_datetime(
                dataframe["check_in_date"]
            ).dt.date
        )

        dataframe["check_out_date"] = (
            pd.to_datetime(
                dataframe["check_out_date"]
            ).dt.date
        )

        dataframe["country_code"] = (
            dataframe["country_code"]
            .fillna("")
            .str.upper()
        )

        dataframe["revenue"] = (
            dataframe["revenue"]
            .fillna(0)
        )

        return dataframe

    def _transform_record(self,record: dict,) -> dict:
        """Apply business rules to a single record."""

        conversion_key = record["conversion_key"]

        record["property_id"] = self._build_property_id(
            record["property_id"]
        )

        record["status"] = self._map_status(
            record["status"]
        )

        record["site_key"] = self._extract_site_key(
            conversion_key
        )

        record["device"] = self._extract_device(
            conversion_key
        )

        record["referral_property_id"] = (
            self._extract_referral_property_id(
                conversion_key
            )
        )

        currency = record.get("currency") or "USD"
        revenue = record.get("revenue") or 0
        record["revenue"] = self._exchange_rate_service.convert_to_usd(
            revenue,
            currency,
        )
        record["currency"] = "USD"

        return record

    def _build_property_id(self,accommodation_id: str | int) -> str:
        """Build property identifier."""

        return (
            f"{self.PROPERTY_PREFIX}-"
            f"{accommodation_id}"
        )

    def _map_status(self, status: str) -> str:
        """Map booking status."""

        return self._status_mapping.get(
            status,
            status,
        )

    def _extract_site_key(self,conversion_key: str) -> str | None:
        """Extract site key."""

        match = re.search(
            r"k-([^_]+)",
            conversion_key,
        )

        if match is None:
            return None

        return match.group(1).upper()

    def _extract_device(self,conversion_key: str) -> str | None:
        """Extract booking device."""

        match = re.search(
            r"d-([^_]+)",
            conversion_key,
        )

        if match is None:
            return None

        return self._device_mapping.get(
            match.group(1)
        )

    def _extract_referral_property_id(self, conversion_key: str) -> str | None:
        """Extract referral property id."""

        match = re.search(
            r"p-([^_]+)",
            conversion_key,
        )

        if match is None:
            return None

        return match.group(1)

    @staticmethod
    def _load_mapping(filename: str) -> dict:
        """Load JSON mapping file."""

        mapping_path = (
            Path(__file__).parent.parent
            / "mappings"
            / filename
        )

        with open(
            mapping_path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)