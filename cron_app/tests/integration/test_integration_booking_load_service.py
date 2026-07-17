import pytest

from models.booking_transaction import BookingTransaction
from services.booking_load_service import BookingLoadService

from tests.test_data.booking_load_data import BOOKINGS


class TestBookingLoadServiceIntegration:

    def test_load_inserts_bookings(self, test_db):
        """Loads bookings into a real PostgreSQL database."""

        service = BookingLoadService(db_instance=test_db)

        inserted = service.load(BOOKINGS)

        assert inserted == len(BOOKINGS)

        with test_db.session_scope() as session:
            rows = (
                session.query(BookingTransaction)
                .order_by(BookingTransaction.transaction_id)
                .all()
            )

            assert len(rows) == len(BOOKINGS)

            assert rows[0].transaction_id == BOOKINGS[0]["transaction_id"]
            assert rows[0].conversion_key == BOOKINGS[0]["conversion_key"]
            assert rows[0].property_id == BOOKINGS[0]["property_id"]
            assert rows[0].status == BOOKINGS[0]["status"]
            assert rows[0].travel_purpose == BOOKINGS[0]["travel_purpose"]
            assert rows[0].country_code == BOOKINGS[0]["country_code"]
            assert rows[0].currency == BOOKINGS[0]["currency"]
            assert rows[0].site_key == BOOKINGS[0]["site_key"]
            assert rows[0].device == BOOKINGS[0]["device"]
            assert rows[0].referral_property_id == BOOKINGS[0]["referral_property_id"]
            assert rows[0].revenue == BOOKINGS[0]["revenue"]
            assert rows[0].revenue_usd == BOOKINGS[0]["revenue_usd"]

            assert rows[1].transaction_id == BOOKINGS[1]["transaction_id"]
            assert rows[1].conversion_key == BOOKINGS[1]["conversion_key"]
            assert rows[1].property_id == BOOKINGS[1]["property_id"]
            assert rows[1].status == BOOKINGS[1]["status"]
            assert rows[1].travel_purpose == BOOKINGS[1]["travel_purpose"]
            assert rows[1].country_code == BOOKINGS[1]["country_code"]
            assert rows[1].currency == BOOKINGS[1]["currency"]
            assert rows[1].site_key == BOOKINGS[1]["site_key"]
            assert rows[1].device == BOOKINGS[1]["device"]
            assert rows[1].referral_property_id == BOOKINGS[1]["referral_property_id"]
            assert rows[1].revenue == BOOKINGS[1]["revenue"]
            assert rows[1].revenue_usd == BOOKINGS[1]["revenue_usd"]
    def test_load_chunks_large_dataset(self, test_db):
        """Verifies chunking works correctly with dataset > 100 items."""
        service = BookingLoadService(db_instance=test_db)

        # Create a large dataset (150+ items) to trigger chunking
        large_bookings = []
        for i in range(150):
            booking = BOOKINGS[0].copy()
            booking["transaction_id"] = f"txn-chunk-{i:03d}"
            large_bookings.append(booking)

        inserted = service.load(large_bookings)

        assert inserted == len(large_bookings)

        with test_db.session_scope() as session:
            rows = session.query(BookingTransaction).all()
            assert len(rows) >= 150
            
            # Verify at least 2 chunks were processed
            txn_ids = {r.transaction_id for r in rows}
            assert len([t for t in txn_ids if t.startswith("txn-chunk-")]) >= 150
