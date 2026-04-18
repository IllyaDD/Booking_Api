from typing import List

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import selectinload
from sqlmodel import select, or_

from common.errors import UnauthorizedAccess
from dependency.session import AsyncSessionDep
from models import Booking
from models.apartaments import Apartment
from models.users import User
from services.bookings.errors import BookingNotFound
from services.bookings.schemas import BookingResponseSchema, BookingShortResponseSchema
from services.apartaments.schemas import ApartmentShortResponseSchema


class BookingQueryBuilder:
    @staticmethod
    async def get_booking_by_id(
        session: AsyncSessionDep, booking_id: int, current_user: User
    ) -> BookingResponseSchema:
        query = (
            select(Booking)
            .where(Booking.id == booking_id)
            .options(selectinload(Booking.apartment).selectinload(Apartment.ratings))
        )
        result = await session.execute(query)
        booking = result.scalar_one_or_none()
        if booking is None:
            raise BookingNotFound(booking_id)

        is_guest = booking.guest_id == current_user.id
        is_owner = booking.apartment.owner_id == current_user.id
        if not (current_user.is_superuser or is_guest or is_owner):
            raise UnauthorizedAccess

        return BookingResponseSchema(
            **booking.model_dump(),
            apartment=ApartmentShortResponseSchema(
                id=booking.apartment.id,
                name=booking.apartment.name,
                type=booking.apartment.type,
                ratings=booking.apartment.ratings_avg,
            ),
        )

    @staticmethod
    async def get_bookings(
        session: AsyncSessionDep, current_user: User
    ) -> Page[BookingShortResponseSchema]:
        if current_user.is_superuser:
            query = select(Booking)
        else:
            query = (
                select(Booking)
                .join(Apartment, Booking.apartment_id == Apartment.id)
                .where(
                    or_(
                        Booking.guest_id == current_user.id,
                        Apartment.owner_id == current_user.id,
                    )
                )
            )

        def transformer(items: List[Booking]) -> List[BookingShortResponseSchema]:
            return [BookingShortResponseSchema(**item.model_dump()) for item in items]

        return await paginate(session, query, transformer=transformer)
