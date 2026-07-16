from unittest.mock import MagicMock, Mock, patch

from models.booking_transaction import BookingTransaction

from services.booking_load_service import BookingLoadService
from tests.test_data.booking_load_data import (
    BOOKINGS,
    EMPTY_BOOKINGS,
    EXISTING_TRANSACTION_IDS,
    NEW_COUNT,
)


class TestBookingLoadService:
    """Tests for BookingLoadService."""

    def test_load_returns_zero_when_bookings_empty(
        self,
        booking_load_service: BookingLoadService,
    ) -> None:
        """Returns zero for empty bookings."""

        result = booking_load_service.load(EMPTY_BOOKINGS)

        assert result == 0

    @patch.object(BookingLoadService, "_persist_chunk")
    def test_load_calls_persist_chunk(
        self,
        mock_persist_chunk: Mock,
        booking_load_service: BookingLoadService,
    ) -> None:
        """Persists booking chunks."""

        mock_persist_chunk.return_value = NEW_COUNT

        result = booking_load_service.load(BOOKINGS)

        mock_persist_chunk.assert_called_once()
        assert result == NEW_COUNT

    def test_get_existing_transaction_ids_empty(
        self,
        booking_load_service: BookingLoadService,
    ) -> None:
        """Returns empty transaction ID set."""

        result = booking_load_service._get_existing_transaction_ids([])

        assert result == set()

    @patch("services.booking_load_service.select")
    def test_get_existing_transaction_ids(
        self,
        mock_select: Mock,
        booking_load_service: BookingLoadService,
    ) -> None:
        """Returns existing transaction IDs."""

        session = Mock()
        session.execute.return_value.scalars.return_value.all.return_value = list(
            EXISTING_TRANSACTION_IDS
        )

        booking_load_service.db.session_scope = MagicMock()
        booking_load_service.db.session_scope.return_value.__enter__.return_value = session
        booking_load_service.db.session_scope.return_value.__exit__.return_value = None

        result = booking_load_service._get_existing_transaction_ids(
            list(EXISTING_TRANSACTION_IDS)
        )

        assert result == EXISTING_TRANSACTION_IDS
        session.execute.assert_called_once()

    def test_merge_booking_row(
        self,
        booking_load_service: BookingLoadService,
    ) -> None:
        """Merges a booking row."""

        session = Mock()

        booking_load_service.db.session_scope = MagicMock()
        booking_load_service.db.session_scope.return_value.__enter__.return_value = session
        booking_load_service.db.session_scope.return_value.__exit__.return_value = None

        booking_load_service._merge_booking_row(BOOKINGS[0])

        session.merge.assert_called_once()

        merged_instance = session.merge.call_args.args[0]
        assert isinstance(merged_instance, BookingTransaction)

    def test_build_instance(
        self,
        booking_load_service: BookingLoadService,
    ) -> None:
        """Builds a booking transaction instance."""

        booking = BOOKINGS[0]

        instance = booking_load_service._build_instance(booking)

        assert isinstance(instance, BookingTransaction)
        assert instance.transaction_id == booking["transaction_id"]
        assert instance.property_id == booking["property_id"]
        assert instance.status == booking["status"]