from extensions import DBService
from models.booking_transaction import BookingTransaction
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError


class BookingLoadService(DBService):

    def __init__(self, db_instance=None):
        super().__init__(db_instance=db_instance)

    def load(self, bookings: list[dict]) -> int:
        # Perform an upsert (insert or update) using PostgreSQL ON CONFLICT
        table = BookingTransaction.__table__

        # Prepare rows to insert (only include known table columns, exclude PK and timestamps)
        cols = {c.name for c in table.columns} - {"id", "created_at", "updated_at"}
        rows = []
        for b in bookings:
            row = {k: v for k, v in b.items() if k in cols}
            rows.append(row)

        if not rows:
            return 0

        insert_stmt = pg_insert(table).values(rows)
        excluded = insert_stmt.excluded
        update_cols = {c: getattr(excluded, c) for c in cols if c != "transaction_id"}
        upsert = insert_stmt.on_conflict_do_update(index_elements=["transaction_id"], set_=update_cols)

        inserted = 0
        try:
            with self.db.engine.begin() as conn:
                result = conn.execute(upsert)
                try:
                    inserted = result.rowcount or 0
                except Exception:
                    inserted = len(rows)
        except SQLAlchemyError:
            # Fallback: insert/update one by one with session merge
            for row in rows:
                try:
                    obj = BookingTransaction(**row)
                    self.db.session.merge(obj)
                    self.db.session.commit()
                    inserted += 1
                except SQLAlchemyError:
                    self.db.session.rollback()
        return inserted

    def _get_existing_transaction_ids(self, transaction_ids: list[str]) -> set:
        if not transaction_ids:
            return set()

        stmt = select(BookingTransaction.transaction_id).where(
            BookingTransaction.transaction_id.in_(transaction_ids)
        )
        rows = self.db.session.execute(stmt).scalars().all()
        return set(rows)

    def _build_instance(self, booking: dict) -> BookingTransaction:
        return BookingTransaction(**booking)