from enum import StrEnum
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, DateTime, Integer, Date
from sqlalchemy.types import Enum as SAEnum
from datetime import datetime, timezone, date

if TYPE_CHECKING:
    from .users import User
    from .apartaments import Apartment


class BookingStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: Optional[int] = Field(default=None, primary_key=True)
    apartment_id: int = Field(nullable=False, foreign_key="apartments.id")
    guest_id: int = Field(nullable=False, foreign_key="users.id")
    check_in: date = Field(sa_column=Column(Date, nullable=False))
    check_out: date = Field(sa_column=Column(Date, nullable=False))
    guests_count: int = Field(sa_column=Column(Integer, nullable=False, default=1))
    status: BookingStatus = Field(
        sa_column=Column(
            SAEnum(BookingStatus), nullable=False, default=BookingStatus.PENDING
        )
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    )

    # Relationships
    apartment: Optional["Apartment"] = Relationship(back_populates="bookings")
    guest: Optional["User"] = Relationship(back_populates="bookings")
