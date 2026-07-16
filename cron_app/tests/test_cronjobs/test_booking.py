import pytest
import requests
from unittest.mock import MagicMock

from cronjobs.booking import BookingCron
from services.booking_extract_service import BookingExtractService
from services.booking_load_service import BookingLoadService
from services.booking_transform_service import BookingTransformService

class TestBookingCron:
    def test_init(self, booking_cron):
        assert booking_cron.updated_from == "2026-07-10"
        assert booking_cron.updated_to == "2026-07-12"

        assert isinstance(
            booking_cron.extract_service,
            BookingExtractService,
        )
        assert isinstance(
            booking_cron.transform_service,
            BookingTransformService,
        )
        assert isinstance(
            booking_cron.load_service,
            BookingLoadService,
        )


    def test_get_query_params(self,booking_cron):
        assert booking_cron.get_query_params() == {
            "updated_from": "2026-07-10",
            "updated_to": "2026-07-12",
        }


    def test_get_query_params_raises_value_error_when_dates_missing(self):
        cron = BookingCron()

        with pytest.raises(
            ValueError,
            match="Both 'updated_from' and 'updated_to' must be provided.",
        ):
            cron.get_query_params()


    def test_fetch_bookings(self, booking_cron, expected_bookings):
        booking_cron.extract_service.fetch = MagicMock(
            return_value=expected_bookings
        )

        result = booking_cron.fetch_bookings()

        booking_cron.extract_service.fetch.assert_called_once_with(
            {
                "updated_from": "2026-07-10",
                "updated_to": "2026-07-12",
            }
        )

        assert result == expected_bookings


    def test_transform_bookings(self, booking_cron,expected_bookings,transformed_bookings):
        booking_cron.transform_service.transform = MagicMock(
            return_value=transformed_bookings
        )

        result = booking_cron.transform_bookings(expected_bookings)

        booking_cron.transform_service.transform.assert_called_once_with(
            expected_bookings
        )

        assert result == transformed_bookings


    def test_load_bookings(self, booking_cron,transformed_bookings):
        booking_cron.load_service.load = MagicMock(
            return_value=2
        )

        result = booking_cron.load_bookings(transformed_bookings)

        booking_cron.load_service.load.assert_called_once_with(
            transformed_bookings
        )

        assert result == 2


    def test_run_success(self, booking_cron, expected_bookings, transformed_bookings):
        booking_cron.fetch_bookings = MagicMock(
            return_value=expected_bookings
        )

        booking_cron.transform_bookings = MagicMock(
            return_value=transformed_bookings
        )

        booking_cron.load_bookings = MagicMock(
            return_value=2
        )

        booking_cron.run()

        booking_cron.fetch_bookings.assert_called_once()
        booking_cron.transform_bookings.assert_called_once_with(
            expected_bookings
        )
        booking_cron.load_bookings.assert_called_once_with(
            transformed_bookings
        )


    def test_run_none_response(self, booking_cron, capsys):
        booking_cron.fetch_bookings = MagicMock(return_value=None)
        booking_cron.transform_bookings = MagicMock()
        booking_cron.load_bookings = MagicMock()

        booking_cron.run()

        captured = capsys.readouterr()

        assert (
            "No booking data received from API: response was empty or null."
            in captured.out
        )

        booking_cron.transform_bookings.assert_not_called()
        booking_cron.load_bookings.assert_not_called()


    def test_run_invalid_response(self, booking_cron, capsys):
        booking_cron.fetch_bookings = MagicMock(return_value={})
        booking_cron.transform_bookings = MagicMock()
        booking_cron.load_bookings = MagicMock()

        booking_cron.run()

        captured = capsys.readouterr()

        assert (
            "No booking data received from API: response was not a list."
            in captured.out
        )

        booking_cron.transform_bookings.assert_not_called()
        booking_cron.load_bookings.assert_not_called()


    def test_run_empty_response(self,booking_cron, capsys):
        booking_cron.fetch_bookings = MagicMock(return_value=[])
        booking_cron.transform_bookings = MagicMock()
        booking_cron.load_bookings = MagicMock()

        booking_cron.run()

        captured = capsys.readouterr()

        assert (
            "No booking data received from API: response was empty."
            in captured.out
        )

        booking_cron.transform_bookings.assert_not_called()
        booking_cron.load_bookings.assert_not_called()


    def test_run_request_exception(self, booking_cron, capsys):
        booking_cron.fetch_bookings = MagicMock(
            side_effect=requests.RequestException(
                "Connection failed"
            )
        )

        booking_cron.run()

        captured = capsys.readouterr()

        assert (
            "API request failed: Connection failed"
            in captured.out
        )