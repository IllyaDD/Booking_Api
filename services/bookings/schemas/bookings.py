from sqlmodel import SQLModel, Field
from datetime import datetime, date
from typing import Optional, List

from models.booking import BookingStatus
from services.apartaments.schemas import ApartmentShortResponseSchema


class BookingShortResponseSchema(SQLModel):
    id: int
    apartment_id: int
    check_in: date
    check_out: date
    status: BookingStatus


class BookingResponseSchema(SQLModel):
    id: int
    apartment_id: int
    guest_id: int
    check_in: date
    check_out: date
    guests_count: int
    status: BookingStatus
    created_at: datetime
    apartment: ApartmentShortResponseSchema


class BookingCreateSchema(SQLModel):
    apartment_id: int
    check_in: date
    check_out: date
    guests_count: int = Field(ge=1)


class BookingUpdateSchema(SQLModel):
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    guests_count: Optional[int] = Field(default=None, ge=1)
    status: Optional[BookingStatus] = None


class BookingListResponseSchema(SQLModel):
    items: List[BookingShortResponseSchema]
