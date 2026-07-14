from extensions import db
from models.booking_transaction import BookingTransaction


class BookingLoadService:
    """Loads transformed bookings into the database."""

    def load(
        self,
        bookings: list[dict],
    ) -> int:
        """Load bookings into the database.

        Returns:
            Number of newly inserted records.
        """

        inserted_count = 0

        for booking in bookings:
            if self._exists(
                booking["transaction_id"]
            ):
                continue

            booking_transaction = (
                BookingTransaction(
                    **booking
                )
            )

            db.session.add(
                booking_transaction
            )

            inserted_count += 1

        db.session.commit()

        return inserted_count

    def _exists(
        self,
        transaction_id: str,
    ) -> bool:
        """Check whether a booking already exists."""

        return (
            db.session.query(
                BookingTransaction.id
            )
            .filter_by(
                transaction_id=transaction_id
            )
            .first()
            is not None
        )