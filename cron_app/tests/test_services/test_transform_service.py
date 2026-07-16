import pandas as pd

from datetime import date
from decimal import Decimal

from services.booking_transform_service import BookingTransformService


class TestBookingTransformService:
    """
    Unit tests for BookingTransformService.
    """

    def test_normalize(
        self,
        booking_transform_service: BookingTransformService,
        bookings: list[dict],
    ) -> None:
        """
        Test booking normalization.
        """
        dataframe = booking_transform_service._normalize(bookings)

        assert isinstance(dataframe, pd.DataFrame)
        assert len(dataframe) == len(bookings)
        assert "label" in dataframe.columns
        assert "status" in dataframe.columns

    def test_prepare_dataframe(
        self,
        booking_transform_service: BookingTransformService,
        bookings: list[dict],
        prepared_record: dict,
    ) -> None:
        """
        Test dataframe preparation.
        """
        dataframe = booking_transform_service._normalize(bookings)

        dataframe = booking_transform_service._prepare_dataframe(
            dataframe,
        )

        record = dataframe.iloc[0].to_dict()

        assert record["transaction_id"] == prepared_record["transaction_id"]
        assert record["conversion_key"] == prepared_record["conversion_key"]
        assert record["property_id"] == prepared_record["property_id"]
        assert record["status"] == prepared_record["status"]
        assert record["travel_purpose"] == prepared_record["travel_purpose"]
        assert record["country_code"] == prepared_record["country_code"]
        assert record["currency"] == prepared_record["currency"]
        assert record["revenue"] == prepared_record["revenue"]

        assert isinstance(
            record["check_in_date"],
            date,
        )

        assert isinstance(
            record["check_out_date"],
            date,
        )

    def test_extract_site_key(
        self,
        booking_transform_service: BookingTransformService,
        conversion_key: str,
        expected_site_key: str,
    ) -> None:
        """
        Test extracting site key.
        """
        result = booking_transform_service._extract_site_key(
            conversion_key,
        )

        assert result == expected_site_key

    def test_extract_site_key_returns_none(
        self,
        booking_transform_service: BookingTransformService,
    ) -> None:
        """
        Test invalid conversion key.
        """
        result = booking_transform_service._extract_site_key(
            "",
        )

        assert result is None

    def test_extract_device(
        self,
        booking_transform_service: BookingTransformService,
        conversion_key: str,
        expected_device: str,
    ) -> None:
        """
        Test extracting device.
        """
        result = booking_transform_service._extract_device(
            conversion_key,
        )

        assert result == expected_device

    def test_extract_device_returns_none(
        self,
        booking_transform_service: BookingTransformService,
    ) -> None:
        """
        Test invalid device.
        """
        result = booking_transform_service._extract_device(
            "",
        )

        assert result is None

    def test_extract_referral_property_id(
        self,
        booking_transform_service: BookingTransformService,
        conversion_key: str,
        expected_referral_property_id: str,
    ) -> None:
        """
        Test extracting referral property id.
        """
        result = (
            booking_transform_service
            ._extract_referral_property_id(
                conversion_key,
            )
        )

        assert result == expected_referral_property_id

    def test_extract_referral_property_id_returns_none(
        self,
        booking_transform_service: BookingTransformService,
    ) -> None:
        """
        Test invalid referral property id.
        """
        result = (
            booking_transform_service
            ._extract_referral_property_id(
                "",
            )
        )

        assert result is None

    def test_to_decimal(
        self,
        booking_transform_service: BookingTransformService,
        expected_decimal: Decimal,
    ) -> None:
        """
        Test decimal conversion.
        """
        result = booking_transform_service._to_decimal(
            100,
        )

        assert result == expected_decimal

    def test_to_decimal_with_none(
        self,
        booking_transform_service: BookingTransformService,
    ) -> None:
        """
        Test decimal conversion with None.
        """
        result = booking_transform_service._to_decimal(
            None,
        )

        assert result == Decimal("0.00")

    def test_transform_record(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
        transformed_record: dict,
        exchange_rate_service,
    ) -> None:
        """
        Test transforming a single booking record.
        """
        result = booking_transform_service._transform_record(
            prepared_record.copy(),
        )

        exchange_rate_service.convert_to_usd.assert_called_once_with(
            100,
            "EUR",
        )

        assert result == transformed_record

    def test_transform(
        self,
        booking_transform_service: BookingTransformService,
        bookings: list[dict],
        transformed_record: dict,
        exchange_rate_service,
    ) -> None:
        """
        Test transforming booking list.
        """
        result = booking_transform_service.transform(bookings)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == transformed_record

        exchange_rate_service.convert_to_usd.assert_called_once_with(
            100,
            "EUR",
        )

    def test_transform_updates_property_prefix(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
    ) -> None:
        """
        Test property id prefix.
        """
        result = booking_transform_service._transform_record(
            prepared_record.copy(),
        )

        assert result["property_id"].startswith(
            BookingTransformService.PROPERTY_PREFIX,
        )

    def test_transform_updates_currency_to_usd(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
    ) -> None:
        """
        Test currency is converted to USD.
        """
        result = booking_transform_service._transform_record(
            prepared_record.copy(),
        )

        assert result["currency"] == "USD"

    def test_transform_status_mapping(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
    ) -> None:
        """
        Test booking status mapping.
        """
        result = booking_transform_service._transform_record(
            prepared_record.copy(),
        )

        assert result["status"] == "Confirmed"

    def test_transform_sets_site_key(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
        expected_site_key: str,
    ) -> None:
        """
        Test extracted site key.
        """
        result = booking_transform_service._transform_record(
            prepared_record.copy(),
        )

        assert result["site_key"] == expected_site_key

    def test_transform_sets_device(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
        expected_device: str,
    ) -> None:
        """
        Test extracted device.
        """
        result = booking_transform_service._transform_record(
            prepared_record.copy(),
        )

        assert result["device"] == expected_device

    def test_transform_sets_referral_property_id(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
        expected_referral_property_id: str,
    ) -> None:
        """
        Test extracted referral property id.
        """
        result = booking_transform_service._transform_record(
            prepared_record.copy(),
        )

        assert (
            result["referral_property_id"]
            == expected_referral_property_id
        )

    def test_transform_converts_revenue_to_decimal(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
        expected_decimal: Decimal,
    ) -> None:
        """
        Test revenue decimal conversion.
        """
        result = booking_transform_service._transform_record(
            prepared_record.copy(),
        )

        assert result["revenue"] == expected_decimal

    def test_transform_converts_revenue_to_usd(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
        expected_usd_amount: Decimal,
    ) -> None:
        """
        Test USD revenue conversion.
        """
        result = booking_transform_service._transform_record(
            prepared_record.copy(),
        )

        assert result["revenue_usd"] == expected_usd_amount

    def test_transform_with_unknown_status(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
    ) -> None:
        """
        Test unmapped status remains unchanged.
        """
        record = prepared_record.copy()
        record["status"] = "pending"

        result = booking_transform_service._transform_record(
            record,
        )

        assert result["status"] == "pending"

    def test_transform_with_missing_conversion_key(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
    ) -> None:
        """
        Test empty conversion key.
        """
        record = prepared_record.copy()
        record["conversion_key"] = ""

        result = booking_transform_service._transform_record(
            record,
        )

        assert result["site_key"] is None
        assert result["device"] is None
        assert result["referral_property_id"] is None

    def test_transform_with_missing_currency(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
        exchange_rate_service,
    ) -> None:
        """
        Test missing currency defaults to USD.
        """
        record = prepared_record.copy()
        record["currency"] = None

        booking_transform_service._transform_record(
            record,
        )

        exchange_rate_service.convert_to_usd.assert_called_once_with(
            100,
            "USD",
        )

    def test_transform_with_missing_revenue(
        self,
        booking_transform_service: BookingTransformService,
        prepared_record: dict,
        exchange_rate_service,
    ) -> None:
        """
        Test missing revenue defaults to zero.
        """
        record = prepared_record.copy()
        record["revenue"] = None

        result = booking_transform_service._transform_record(
            record,
        )

        exchange_rate_service.convert_to_usd.assert_called_once_with(
            0,
            "EUR",
        )

        assert result["revenue"] == Decimal("0.00")