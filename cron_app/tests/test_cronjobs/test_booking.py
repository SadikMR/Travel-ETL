import pytest
import requests
from unittest.mock import MagicMock

from cronjobs.booking import BookingCron
from services.booking_extract_service import BookingExtractService
from services.booking_load_service import BookingLoadService
from services.booking_transform_service import BookingTransformService
from tests.test_data.booking_cron_data import (
    API_REQUEST_FAILED_MESSAGE,
    CONNECTION_ERROR,
    EMPTY_DICT,
    EMPTY_LIST,
    LOADED_COUNT,
    NO_DATA_EMPTY_MESSAGE,
    NO_DATA_INVALID_MESSAGE,
    NO_DATA_NULL_MESSAGE,
    NONE_VALUE,
    QUERY_PARAMS,
    TRANSFORMED_BOOKINGS,
    VALUE_ERROR_MESSAGE,
)
from tests.test_data.common_data import (
    BOOKINGS,
    UPDATED_FROM,
    UPDATED_TO,
)


class TestBookingCron:
    """Unit tests for BookingCron."""

    # Verify cron object is initialized correctly.
    def test_init(
        self,
        booking_cron: BookingCron,
    ) -> None:
        assert booking_cron.updated_from == UPDATED_FROM
        assert booking_cron.updated_to == UPDATED_TO

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

    # Verify query parameters are generated correctly.
    def test_get_query_params(
        self,
        booking_cron: BookingCron,
    ) -> None:
        assert booking_cron.get_query_params() == QUERY_PARAMS

    # Verify missing dates raise a ValueError.
    def test_get_query_params_raises_value_error_when_dates_missing(
        self,
    ) -> None:
        cron = BookingCron()

        with pytest.raises(
            ValueError,
            match=VALUE_ERROR_MESSAGE,
        ):
            cron.get_query_params()

    # Verify bookings are fetched through the extract service.
    def test_fetch_bookings(
        self,
        booking_cron: BookingCron,
        expected_bookings: list[dict],
    ) -> None:
        booking_cron.extract_service.fetch = MagicMock(
            return_value=expected_bookings,
        )

        result = booking_cron.fetch_bookings()

        booking_cron.extract_service.fetch.assert_called_once_with(
            QUERY_PARAMS,
        )

        assert result == expected_bookings

    # Verify bookings are transformed correctly.
    def test_transform_bookings(
        self,
        booking_cron: BookingCron,
        expected_bookings: list[dict],
        transformed_bookings: list[dict],
    ) -> None:
        booking_cron.transform_service.transform = MagicMock(
            return_value=transformed_bookings,
        )

        result = booking_cron.transform_bookings(
            expected_bookings,
        )

        booking_cron.transform_service.transform.assert_called_once_with(
            expected_bookings,
        )

        assert result == transformed_bookings

    # Verify transformed bookings are loaded.
    def test_load_bookings(
        self,
        booking_cron: BookingCron,
        transformed_bookings: list[dict],
    ) -> None:
        booking_cron.load_service.load = MagicMock(
            return_value=LOADED_COUNT,
        )

        result = booking_cron.load_bookings(
            transformed_bookings,
        )

        booking_cron.load_service.load.assert_called_once_with(
            transformed_bookings,
        )

        assert result == LOADED_COUNT

    # Verify the complete cron workflow executes successfully.
    def test_run_success(
        self,
        booking_cron: BookingCron,
        expected_bookings: list[dict],
        transformed_bookings: list[dict],
    ) -> None:
        booking_cron.fetch_bookings = MagicMock(
            return_value=expected_bookings,
        )
        booking_cron.transform_bookings = MagicMock(
            return_value=transformed_bookings,
        )
        booking_cron.load_bookings = MagicMock(
            return_value=LOADED_COUNT,
        )

        booking_cron.run()

        booking_cron.fetch_bookings.assert_called_once()
        booking_cron.transform_bookings.assert_called_once_with(
            expected_bookings,
        )
        booking_cron.load_bookings.assert_called_once_with(
            transformed_bookings,
        )

    # Verify processing stops when API returns None.
    def test_run_none_response(
        self,
        booking_cron: BookingCron,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        booking_cron.fetch_bookings = MagicMock(
            return_value=NONE_VALUE,
        )
        booking_cron.transform_bookings = MagicMock()
        booking_cron.load_bookings = MagicMock()

        booking_cron.run()

        captured = capsys.readouterr()

        assert NO_DATA_NULL_MESSAGE in captured.out
        booking_cron.transform_bookings.assert_not_called()
        booking_cron.load_bookings.assert_not_called()

    # Verify processing stops when API returns an invalid type.
    def test_run_invalid_response(
        self,
        booking_cron: BookingCron,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        booking_cron.fetch_bookings = MagicMock(
            return_value=EMPTY_DICT,
        )
        booking_cron.transform_bookings = MagicMock()
        booking_cron.load_bookings = MagicMock()

        booking_cron.run()

        captured = capsys.readouterr()

        assert NO_DATA_INVALID_MESSAGE in captured.out
        booking_cron.transform_bookings.assert_not_called()
        booking_cron.load_bookings.assert_not_called()

    # Verify processing stops when API returns an empty list.
    def test_run_empty_response(
        self,
        booking_cron: BookingCron,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        booking_cron.fetch_bookings = MagicMock(
            return_value=EMPTY_LIST,
        )
        booking_cron.transform_bookings = MagicMock()
        booking_cron.load_bookings = MagicMock()

        booking_cron.run()

        captured = capsys.readouterr()

        assert NO_DATA_EMPTY_MESSAGE in captured.out
        booking_cron.transform_bookings.assert_not_called()
        booking_cron.load_bookings.assert_not_called()

    # Verify request exceptions are handled gracefully.
    def test_run_request_exception(
        self,
        booking_cron: BookingCron,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        booking_cron.fetch_bookings = MagicMock(
            side_effect=requests.RequestException(
                CONNECTION_ERROR,
            ),
        )

        booking_cron.run()

        captured = capsys.readouterr()

        assert API_REQUEST_FAILED_MESSAGE in captured.out