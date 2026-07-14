from extensions import DBService
from models.booking_transaction import BookingTransaction
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError


class BookingLoadService(DBService):

    def __init__(self, db_instance=None):
        super().__init__(db_instance=db_instance)

    def load(self, bookings: list[dict]) -> int:
        table = BookingTransaction.__table__

        # Prepare rows to insert (only include known table columns, exclude PK and timestamps)
        cols = {c.name for c in table.columns} - {"id", "created_at", "updated_at"}
        rows = []
        for b in bookings:
            row = {k: v for k, v in b.items() if k in cols}
            rows.append(row)

        if not rows:
            return 0

        inserted = 0
        chunk_size = 100

        for start in range(0, len(rows), chunk_size):
            chunk_rows = rows[start:start + chunk_size]
            inserted += self._persist_chunk(chunk_rows=chunk_rows, table=table, cols=cols)

        return inserted

    def _persist_chunk(self, chunk_rows: list[dict], table, cols) -> int:
        insert_stmt = pg_insert(table).values(chunk_rows)
        excluded = insert_stmt.excluded
        update_cols = {c: getattr(excluded, c) for c in cols if c != "transaction_id"}
        upsert = insert_stmt.on_conflict_do_update(index_elements=["transaction_id"], set_=update_cols)

        try:
            with self.db.engine.begin() as conn:
                result = conn.execute(upsert)
                try:
                    return result.rowcount or len(chunk_rows)
                except Exception:
                    return len(chunk_rows)
        except SQLAlchemyError:
            persisted = 0
            for row in chunk_rows:
                try:
                    self._merge_booking_row(row)
                    persisted += 1
                except SQLAlchemyError:
                    continue
            return persisted

    def _merge_booking_row(self, row: dict) -> None:
        with self.db.session.begin():
            self.db.session.merge(BookingTransaction(**row))

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