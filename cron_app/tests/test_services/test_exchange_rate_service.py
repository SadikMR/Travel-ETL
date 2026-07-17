import requests
from unittest.mock import Mock

from services.exchange_rate_service import ExchangeRateService
from tests.test_data.exchange_rate_data import (
    AMOUNT,
    DEFAULT_RATE,
    EMPTY_RESPONSE,
    EUR,
    INVALID_RESPONSE,
    SUCCESS_RESPONSE,
    SUCCESS_RESPONSE_NO_USD,
    USD,
    USD_RATE,
)


class TestExchangeRateService:
    """Tests for ExchangeRateService."""

    def test_init(
        self,
        exchange_service: ExchangeRateService,
        mock_session: Mock,
    ) -> None:
        """Initialize service."""

        assert exchange_service._session is mock_session
        assert exchange_service._rate_cache == {}

    def test_convert_to_usd_returns_same_amount_for_usd(
        self,
        exchange_service: ExchangeRateService,
    ) -> None:
        """Skip conversion for USD."""

        result = exchange_service.convert_to_usd(AMOUNT, USD)

        assert result == AMOUNT

    def test_convert_to_usd_uses_cached_rate(
        self,
        exchange_service: ExchangeRateService,
    ) -> None:
        """Use cached rate."""

        exchange_service._rate_cache[EUR] = USD_RATE

        result = exchange_service.convert_to_usd(AMOUNT, EUR)

        assert result == AMOUNT * USD_RATE

    def test_convert_to_usd_fetches_and_caches_rate(
        self,
        exchange_service: ExchangeRateService,
    ) -> None:
        """Fetch and cache rate."""

        exchange_service._fetch_rate = Mock(return_value=USD_RATE)

        result = exchange_service.convert_to_usd(AMOUNT, EUR)

        assert result == AMOUNT * USD_RATE
        assert exchange_service._rate_cache[EUR] == USD_RATE
        exchange_service._fetch_rate.assert_called_once_with(EUR)

    def test_fetch_rate_returns_rate_on_success(
        self,
        exchange_service: ExchangeRateService,
        mock_session: Mock,
        mock_response: Mock,
    ) -> None:
        """Return rate from API."""

        mock_session.get.return_value = mock_response

        rate = exchange_service._fetch_rate(EUR)

        assert rate == USD_RATE
        mock_session.get.assert_called_once()

    def test_fetch_rate_returns_default_on_request_error(
        self,
        exchange_service: ExchangeRateService,
        mock_session: Mock,
    ) -> None:
        """Return default rate on request error."""

        mock_session.get.side_effect = requests.RequestException()

        rate = exchange_service._fetch_rate(EUR)

        assert rate == DEFAULT_RATE

    def test_extract_usd_rate_returns_rate(self) -> None:
        """Extract USD rate."""

        assert (
            ExchangeRateService._extract_usd_rate(SUCCESS_RESPONSE)
            == USD_RATE
        )

    def test_extract_usd_rate_returns_none_when_usd_missing(
        self,
    ) -> None:
        """Handle missing USD."""

        assert (
            ExchangeRateService._extract_usd_rate(
                SUCCESS_RESPONSE_NO_USD
            )
            is None
        )

    def test_extract_usd_rate_returns_none_for_invalid_payload(
        self,
    ) -> None:
        """Handle invalid payload."""

        assert (
            ExchangeRateService._extract_usd_rate(
                INVALID_RESPONSE
            )
            is None
        )

    def test_extract_usd_rate_returns_none_for_empty_payload(
        self,
    ) -> None:
        """Handle empty payload."""

        assert (
            ExchangeRateService._extract_usd_rate(
                EMPTY_RESPONSE
            )
            is None
        )

    def test_build_request(
        self,
        exchange_service: ExchangeRateService,
    ) -> None:
        """Build request URL."""

        url, params = exchange_service._build_request(EUR)

        assert url.endswith(f"/{EUR}")
        assert params == {}