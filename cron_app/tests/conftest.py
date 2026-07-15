import pytest

from cronjobs.booking import BookingCron


@pytest.fixture
def booking_cron():
    return BookingCron(
        updated_from="2026-07-10",
        updated_to="2026-07-12",
    )


@pytest.fixture
def expected_bookings():
    return [
        {"id": "1"},
        {"id": "2"},
    ]


@pytest.fixture
def transformed_bookings():
    return [
        {"booking_id": "1"},
        {"booking_id": "2"},
    ]