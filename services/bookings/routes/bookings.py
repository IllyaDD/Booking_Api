from dependency.session import AsyncSessionDep
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page

from common.errors import UnauthorizedAccess
from models.users import User
from services.apartaments.errors import ApartamentsNotFound
from services.bookings.errors import (
    BookingNotFound,
    Cant_book_in_past,
    Checkin_earlier_than_Chekout,
    Dated_Already_Booked,
    GuestsCountExceedsCapacity,
)
from services.bookings.query_builder.bookings import BookingQueryBuilder
from services.bookings.schemas import BookingResponseSchema, BookingShortResponseSchema
from services.bookings.schemas.bookings import BookingCreateSchema, BookingUpdateSchema
from services.users.modules.manager import current_active_user

bookings_router = APIRouter()


@bookings_router.post(
    "/bookings/",
    response_model=BookingShortResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    booking_data: BookingCreateSchema,
    session: AsyncSessionDep,
    current_user: User = Depends(current_active_user),
):
    try:
        return await BookingQueryBuilder.create_booking(
            session, current_user, booking_data
        )
    except ApartamentsNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Checkin_earlier_than_Chekout as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Dated_Already_Booked as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Cant_book_in_past as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except GuestsCountExceedsCapacity as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@bookings_router.get("/bookings/", response_model=Page[BookingShortResponseSchema])
async def get_bookings(
    session: AsyncSessionDep,
    current_user: User = Depends(current_active_user),
):
    return await BookingQueryBuilder.get_bookings(session, current_user)


@bookings_router.get("/bookings/{booking_id}", response_model=BookingResponseSchema)
async def get_booking_by_id(
    session: AsyncSessionDep,
    booking_id: int,
    current_user: User = Depends(current_active_user),
):
    try:
        return await BookingQueryBuilder.get_booking_by_id(
            session, booking_id, current_user
        )
    except BookingNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )


@bookings_router.patch(
    "/bookings/{booking_id}", response_model=BookingShortResponseSchema
)
async def update_booking(
    booking_id: int,
    update_data: BookingUpdateSchema,
    session: AsyncSessionDep,
    current_user: User = Depends(current_active_user),
):
    try:
        return await BookingQueryBuilder.update_booking(
            session, booking_id, current_user, update_data
        )
    except BookingNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    except Checkin_earlier_than_Chekout as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Dated_Already_Booked as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Cant_book_in_past as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except GuestsCountExceedsCapacity as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@bookings_router.delete(
    "/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_booking(
    booking_id: int,
    session: AsyncSessionDep,
    current_user: User = Depends(current_active_user),
):
    try:
        await BookingQueryBuilder.delete_booking(session, booking_id, current_user)
    except BookingNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedAccess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
