import pytest
from requests.exceptions import HTTPError
from unittest.mock import Mock, patch

from cron_app.services.booking_extract_service import BookingExtractService
from tests.test_data.booking_extract_data import (
    ENDPOINT,
    HTTP_ERROR_MESSAGE,
    REQUEST_TIMEOUT,
    URL,
)


class TestBookingExtractService:
    """Unit tests for BookingExtractService."""

    # Verify service is initialized correctly.
    def test_init(
        self,
        booking_extract_service: BookingExtractService,
    ) -> None:
        assert booking_extract_service.base_url is not None
        assert booking_extract_service.endpoint == ENDPOINT

    # Verify the request URL is built correctly.
    def test_build_url(
        self,
        booking_extract_service: BookingExtractService,
    ) -> None:
        assert booking_extract_service._build_url() == URL

    # Verify requests.get is called with expected arguments.
    @patch("cron_app.services.booking_extract_service.requests.get")
    def test_request(
        self,
        mock_get: Mock,
        booking_extract_service: BookingExtractService,
        valid_params: dict[str, str],
    ) -> None:
        booking_extract_service._request(valid_params)

        mock_get.assert_called_once_with(
            url=URL,
            params=valid_params,
            timeout=REQUEST_TIMEOUT,
        )

    # Verify bookings are returned on a successful request.
    @patch("cron_app.services.booking_extract_service.requests.get")
    def test_fetch_success(
        self,
        mock_get: Mock,
        booking_extract_service: BookingExtractService,
        valid_params: dict[str, str],
        success_response: list[dict],
    ) -> None:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = success_response

        mock_get.return_value = mock_response

        result = booking_extract_service.fetch(valid_params)

        assert result == success_response
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

    # Verify HTTP errors are propagated.
    @patch("cron_app.services.booking_extract_service.requests.get")
    def test_fetch_http_error(
        self,
        mock_get: Mock,
        booking_extract_service: BookingExtractService,
        valid_params: dict[str, str],
    ) -> None:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError(
            HTTP_ERROR_MESSAGE,
        )

        mock_get.return_value = mock_response

        with pytest.raises(
            HTTPError,
            match=HTTP_ERROR_MESSAGE,
        ):
            booking_extract_service.fetch(valid_params)