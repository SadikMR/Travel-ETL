from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

from extensions import Base


class BookingTransaction(Base):
    __tablename__ = "booking_transactions"

    id = Column(Integer, primary_key=True)

    transaction_id = Column(
        String(50),
        unique=True,
        nullable=False,
    )

    conversion_key = Column(String(255), nullable=False)

    property_id = Column(String(100), nullable=False)

    status = Column(String(50))

    travel_purpose = Column(String(50))

    country_code = Column(String(10))

    currency = Column(String(10))

    check_in_date = Column(Date)

    check_out_date = Column(Date)

    site_key = Column(String(20))

    device = Column(String(20))

    referral_property_id = Column(String(100))

    revenue = Column(Numeric(10, 2), default=Decimal("0.00"))

    revenue_usd = Column(Numeric(10, 2), default=Decimal("0.00"))

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )