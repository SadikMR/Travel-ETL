import pytest

from unittest.mock import Mock

from cronjobs.booking import BookingCron
from services.booking_extract_service import BookingExtractService
from services.exchange_rate_service import ExchangeRateService

from tests.test_data.common_data import (
    BOOKINGS,
    QUERY_PARAMS,
    TRANSFORMED_BOOKINGS,
)

from tests.test_data.booking_extract_data import (
    BASE_URL,
    ENDPOINT,
    VALID_PARAMS,
    SUCCESS_RESPONSE as BOOKING_SUCCESS_RESPONSE,
)

from tests.test_data.exchange_rate_data import (
    SUCCESS_RESPONSE as EXCHANGE_RATE_SUCCESS_RESPONSE,
)

# BookingCron

@pytest.fixture(scope="session")
def booking_cron() -> BookingCron:
    return BookingCron(
        updated_from=QUERY_PARAMS["updated_from"],
        updated_to=QUERY_PARAMS["updated_to"],
    )


@pytest.fixture(scope="session")
def expected_bookings() -> list[dict]:
    return BOOKINGS


@pytest.fixture(scope="session")
def transformed_bookings() -> list[dict]:
    return TRANSFORMED_BOOKINGS



# BookingExtractService


@pytest.fixture(scope="session")
def booking_extract_service() -> BookingExtractService:
    return BookingExtractService(
        base_url=BASE_URL,
        endpoint=ENDPOINT,
    )


@pytest.fixture(scope="session")
def valid_params() -> dict[str, str]:
    return VALID_PARAMS


@pytest.fixture(scope="session")
def success_response() -> list[dict]:
    return BOOKING_SUCCESS_RESPONSE


# ExchangeRateService

@pytest.fixture
def mock_session() -> Mock:
    return Mock()


@pytest.fixture
def mock_response() -> Mock:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = EXCHANGE_RATE_SUCCESS_RESPONSE
    return response


@pytest.fixture
def exchange_service(
    mock_session: Mock,
) -> ExchangeRateService:
    return ExchangeRateService(session=mock_session)