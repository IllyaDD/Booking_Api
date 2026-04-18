from dependency.session import AsyncSessionDep
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page

from common.errors import UnauthorizedAccess
from models.users import User
from services.bookings.errors import BookingNotFound
from services.bookings.query_builder.bookings import BookingQueryBuilder
from services.bookings.schemas import BookingResponseSchema, BookingShortResponseSchema
from services.users.modules.manager import current_active_user

bookings_router = APIRouter()


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
