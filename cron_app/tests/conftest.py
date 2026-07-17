import pytest

from decimal import Decimal
from unittest.mock import Mock, MagicMock
from contextlib import contextmanager

from cronjobs.booking import BookingCron
from services.booking_extract_service import BookingExtractService
from services.booking_transform_service import BookingTransformService
from services.exchange_rate_service import ExchangeRateService

from services.booking_load_service import BookingLoadService

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

from tests.test_data.booking_transform_data import (
    BOOKINGS as RAW_BOOKINGS,
    CONVERSION_KEY,
    DECIMAL_VALUE,
    DEVICE,
    PREPARED_RECORD,
    REFERRAL_PROPERTY_ID,
    SITE_KEY,
    TRANSFORMED_RECORD,
    USD_AMOUNT,
)

from extensions import Base, Database


TEST_DATABASE_URI = (
    "postgresql://postgres:postgres@localhost:5432/travel_test"
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


# BookingTransformService

@pytest.fixture
def exchange_rate_service() -> Mock:
    """
    Mock ExchangeRateService used by BookingTransformService.
    """
    service = Mock(spec=ExchangeRateService)
    service.convert_to_usd.return_value = USD_AMOUNT
    return service


@pytest.fixture
def booking_transform_service(
    exchange_rate_service: Mock,
) -> BookingTransformService:
    """
    BookingTransformService with mocked dependencies.
    """
    service = BookingTransformService(
        exchange_rate_service=exchange_rate_service,
    )

    # Override mapping files so tests are deterministic.
    service._status_mapping = {
        "ok": "Confirmed",
    }

    service._device_mapping = {
        "mobile": DEVICE,
    }

    return service


@pytest.fixture
def bookings() -> list[dict]:
    """
    Raw booking payload.
    """
    return RAW_BOOKINGS


@pytest.fixture
def conversion_key() -> str:
    return CONVERSION_KEY


@pytest.fixture
def prepared_record() -> dict:
    return PREPARED_RECORD.copy()


@pytest.fixture
def transformed_record() -> dict:
    return TRANSFORMED_RECORD.copy()


@pytest.fixture
def expected_site_key() -> str:
    return SITE_KEY


@pytest.fixture
def expected_device() -> str:
    return DEVICE


@pytest.fixture
def expected_referral_property_id() -> str:
    return REFERRAL_PROPERTY_ID


@pytest.fixture
def expected_decimal() -> Decimal:
    return DECIMAL_VALUE


@pytest.fixture
def expected_usd_amount() -> Decimal:
    return USD_AMOUNT


# BookingLoadService

@pytest.fixture
def db_instance() -> Mock:
    """Mock database instance."""

    db = Mock()

    @contextmanager
    def session_scope():
        session = MagicMock()  # pragma: no cover
        yield session  # pragma: no cover

    db.session_scope = session_scope

    return db


@pytest.fixture
def booking_load_service(
    db_instance: Mock,
) -> BookingLoadService:
    """BookingLoadService with mocked database."""

    return BookingLoadService(db_instance=db_instance)


@pytest.fixture
def test_db():
    db = Database(TEST_DATABASE_URI)
    db.initialize()

    Base.metadata.create_all(db.engine)

    yield db

    Base.metadata.drop_all(db.engine)  # pragma: no cover
