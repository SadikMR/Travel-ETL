from datetime import datetime, timezone

try:
    from ..extensions import db
except ImportError:
    from extensions import db


class BookingTransaction(db.Model):
    __tablename__ = "booking_transactions"

    id = db.Column(db.Integer, primary_key=True)

    transaction_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
    )

    conversion_key = db.Column(db.String(255), nullable=False)

    property_id = db.Column(db.String(100), nullable=False)

    status = db.Column(db.String(50))

    travel_purpose = db.Column(db.String(50))

    country_code = db.Column(db.String(10))

    currency = db.Column(db.String(10))

    check_in_date = db.Column(db.Date)

    check_out_date = db.Column(db.Date)

    site_key = db.Column(db.String(20))

    device = db.Column(db.String(20))

    referral_property_id = db.Column(db.String(100))

    revenue = db.Column(db.Float, default=0)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )