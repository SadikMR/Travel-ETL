from extensions import db
from models.booking_transaction import BookingTransaction
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


class BookingLoadService:

    def load(self, bookings: list[dict]) -> int:
        transaction_ids = [b["transaction_id"] for b in bookings]
        existing = self._get_existing_transaction_ids(transaction_ids)

        new_bookings = [b for b in bookings if b["transaction_id"] not in existing]
        instances = [self._build_instance(b) for b in new_bookings]

        inserted = 0
        if instances:
            try:
                db.session.bulk_save_objects(instances)
                db.session.commit()
                inserted = len(instances)
            except SQLAlchemyError:
                db.session.rollback()
                for inst in instances:
                    db.session.add(inst)
                db.session.commit()
                inserted = len(instances)

        return inserted

    def _get_existing_transaction_ids(self, transaction_ids: list[str]) -> set:
        if not transaction_ids:
            return set()

        stmt = select(BookingTransaction.transaction_id).where(
            BookingTransaction.transaction_id.in_(transaction_ids)
        )
        rows = db.session.execute(stmt).scalars().all()
        return set(rows)

    def _build_instance(self, booking: dict) -> BookingTransaction:
        return BookingTransaction(**booking)