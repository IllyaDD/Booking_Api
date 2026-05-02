from datetime import date
from typing import List

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import selectinload
from sqlmodel import select, or_

from common.errors import UnauthorizedAccess
from dependency.session import AsyncSessionDep
from models import Booking
from models.booking import BookingStatus
from models.apartaments import Apartment
from models.users import User
from services.apartaments.errors import ApartamentsNotFound
from services.apartaments.schemas import ApartmentShortResponseSchema
from services.bookings.errors import (
    BookingNotFound,
    Cant_book_in_past,
    Checkin_earlier_than_Chekout,
    Dated_Already_Booked,
    GuestsCountExceedsCapacity,
)
from services.bookings.schemas import BookingResponseSchema, BookingShortResponseSchema
from services.bookings.schemas.bookings import BookingCreateSchema, BookingUpdateSchema


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

    @staticmethod
    async def create_booking(
        session: AsyncSessionDep,
        current_user: User,
        booking_data: BookingCreateSchema,
    ):
        apartament = await session.scalar(
            select(Apartment)
            .where(Apartment.id == booking_data.apartment_id)
            .with_for_update()
        )
        if not apartament:
            raise ApartamentsNotFound(booking_data.apartment_id)

        await BookingQueryBuilder.validate_booking(apartament, booking_data, session)

        booking = Booking(**booking_data.model_dump(), guest_id=current_user.id)
        session.add(booking)
        await session.commit()
        return booking

    @staticmethod
    async def update_booking(
        session: AsyncSessionDep,
        booking_id: int,
        current_user: User,
        update_data: BookingUpdateSchema,
    ) -> BookingShortResponseSchema:
        booking = await session.get(Booking, booking_id)
        if booking is None:
            raise BookingNotFound(booking_id)
        if not (current_user.is_superuser or booking.guest_id == current_user.id):
            raise UnauthorizedAccess

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(booking, key, value)

        needs_validation = any(
            k in update_dict for k in ("check_in", "check_out", "guests_count")
        )
        if needs_validation and booking.status != BookingStatus.CANCELLED:
            apartament = await session.get(Apartment, booking.apartment_id)
            validate_data = BookingCreateSchema(
                apartment_id=booking.apartment_id,
                check_in=booking.check_in,
                check_out=booking.check_out,
                guests_count=booking.guests_count,
            )
            await BookingQueryBuilder.validate_booking(
                apartament, validate_data, session, exclude_id=booking_id
            )

        await session.commit()
        await session.refresh(booking)
        return BookingShortResponseSchema(**booking.model_dump())

    @staticmethod
    async def delete_booking(
        session: AsyncSessionDep,
        booking_id: int,
        current_user: User,
    ) -> None:
        booking = await session.get(Booking, booking_id)
        if booking is None:
            raise BookingNotFound(booking_id)
        if not (current_user.is_superuser or booking.guest_id == current_user.id):
            raise UnauthorizedAccess

        await session.delete(booking)
        await session.commit()

    @staticmethod
    async def validate_booking(
        apartaments: Apartment,
        booking_data: BookingCreateSchema,
        session: AsyncSessionDep,
        exclude_id: int | None = None,
    ):
        if booking_data.check_in >= booking_data.check_out:
            raise Checkin_earlier_than_Chekout
        if booking_data.check_in < date.today():
            raise Cant_book_in_past
        if booking_data.guests_count > apartaments.max_guests:
            raise GuestsCountExceedsCapacity(
                booking_data.guests_count, apartaments.max_guests
            )

        overlap_query = select(Booking).where(
            Booking.apartment_id == apartaments.id,
            Booking.status != BookingStatus.CANCELLED,
            Booking.check_in < booking_data.check_out,
            Booking.check_out > booking_data.check_in,
        )
        if exclude_id is not None:
            overlap_query = overlap_query.where(Booking.id != exclude_id)

        if await session.scalar(overlap_query):
            raise Dated_Already_Booked
