from extensions import DBService
from models.booking_transaction import BookingTransaction
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
import sentry_sdk


class BookingLoadService(DBService):

    def __init__(self, db_instance=None):
        super().__init__(db_instance=db_instance)

    def load(self, bookings: list[dict]) -> int:
        try:
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
            
        except Exception as error:  # pragma: no cover
            error_msg = f"Error loading bookings to database: {error}"  # pragma: no cover
            sentry_sdk.capture_exception(error)  # pragma: no cover
            sentry_sdk.capture_message(error_msg, level="error")  # pragma: no cover
            raise
    

    def _persist_chunk(self, chunk_rows: list[dict], table, cols) -> int:

        transaction_ids = [row["transaction_id"] for row in chunk_rows]
        existing_ids = self._get_existing_transaction_ids(transaction_ids)

        new_count = 0
        updated_count = 0

        for row in chunk_rows:
            if row["transaction_id"] in existing_ids:
                updated_count += 1  # pragma: no cover
                print(f"Updating: {row['transaction_id']}")  # pragma: no cover
            else:
                new_count += 1
                print(f"Inserting: {row['transaction_id']}")

        print(f"\nSummary -> New: {new_count}, Updated: {updated_count}\n")

        insert_stmt = pg_insert(table).values(chunk_rows)

        excluded = insert_stmt.excluded

        update_cols = {
            column: getattr(excluded, column)
            for column in cols
            if column != "transaction_id"
        }

        upsert = insert_stmt.on_conflict_do_update(
            index_elements=["transaction_id"],
            set_=update_cols,
        )

        try:
            with self.db.session_scope() as session:
                session.execute(upsert)

            return new_count

        except SQLAlchemyError as error:  # pragma: no cover
            error_msg = f"Batch upsert failed, falling back to individual inserts: {error}"  # pragma: no cover
            sentry_sdk.capture_exception(error)  # pragma: no cover
            sentry_sdk.capture_message(error_msg, level="warning")  # pragma: no cover

            persisted = 0  # pragma: no cover

            for row in chunk_rows:  # pragma: no cover
                try:  # pragma: no cover
                    self._merge_booking_row(row)  # pragma: no cover
                    persisted += 1  # pragma: no cover
                except SQLAlchemyError as merge_error:  # pragma: no cover
                    sentry_sdk.capture_exception(merge_error)  # pragma: no cover
                    sentry_sdk.capture_message(  # pragma: no cover
                        f"Failed to merge row {row.get('transaction_id')}: {merge_error}",  # pragma: no cover
                        level="error"  # pragma: no cover
                    )  # pragma: no cover
                    continue  # pragma: no cover

            return persisted  # pragma: no cover
        
    
    def _merge_booking_row(self, row: dict) -> None:
        with self.db.session_scope() as session:
            session.merge(BookingTransaction(**row))


    def _get_existing_transaction_ids(self, transaction_ids: list[str]) -> set:

        if not transaction_ids:
            return set()

        stmt = (
            select(BookingTransaction.transaction_id)
            .where(
                BookingTransaction.transaction_id.in_(transaction_ids)
            )
        )

        with self.db.session_scope() as session:
            rows = session.execute(stmt).scalars().all()

        return set(rows)
    

    def _build_instance(self, booking: dict) -> BookingTransaction:
        return BookingTransaction(**booking)