from typing import Optional

from dependency import session
from dependency.session import AsyncSessionDep
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi_pagination import Page

from models import apartaments
from models.apartaments import ApartmentType
from models.users import User
from services.apartaments.errors import (
    ApartamentsNotFound,
    ApartamentAlreadyExists,
    InvalidFilters,
)
from services.apartaments.schemas.apartaments import (
    ApartmentCreateSchema,
    ApartmentResponseSchema,
    ApartmentShortResponseSchema,
    ApartmentUpdateSchema,
)
from services.users.modules.manager import current_active_user
from services.apartaments.query_builder.apartaments import ApartamentQueryBuilder

from common.errors import UnauthorizedAccess
from common.cache import cache

apartament_router = APIRouter()


@apartament_router.get(
    "/apartaments/", response_model=Page[ApartmentShortResponseSchema]
)
@cache(expire=300)
async def get_apartaments(
    session: AsyncSessionDep,
    name: str = Query(None, description="Filter by name"),
    type: ApartmentType = Query(None, description="Filter by type of apartments"),
    min_rooms: int = Query(None, description="Filter by min rooms in your apartments"),
    max_rooms: int = Query(None, description="Filter by max rooms in your apartments"),
    min_guests: int = Query(
        None, description="Filter by min ampunt of guests in tour apartments"
    ),
    max_guests: int = Query(
        None, description="Filter by min ampunt of guests in tour apartments"
    ),
):
    try:
        return await ApartamentQueryBuilder.get_apartaments(
            session,
            name=name,
            type=type,
            min_rooms=min_rooms,
            max_rooms=max_rooms,
            min_guests=min_guests,
            max_guests=max_guests,
        )
    except InvalidFilters as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@apartament_router.post(
    "/apartaments/",
    status_code=status.HTTP_201_CREATED,
    response_model=ApartmentResponseSchema,
)
async def create_apartament(
    session: AsyncSessionDep,
    apartament_data: ApartmentCreateSchema,
    current_user: User = Depends(current_active_user),
):
    try:
        return await ApartamentQueryBuilder.create_apartament(
            session, user_id=current_user.id, apartament_data=apartament_data
        )
    except ApartamentAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@apartament_router.get(
    "/apartaments/{apartament_id}", response_model=ApartmentResponseSchema
)
async def get_apartament_by_id(session: AsyncSessionDep, apartament_id: int):
    try:
        return await ApartamentQueryBuilder.get_apartament_by_id(session, apartament_id)
    except ApartamentsNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@apartament_router.delete(
    "/apartaments/{apartament_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_apartament(
    session: AsyncSessionDep,
    apartament_id: int,
    user: User = Depends(current_active_user),
):
    try:
        await ApartamentQueryBuilder.delete_apartament(session, user.id, apartament_id)
    except ApartamentsNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedAccess as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@apartament_router.patch("/apartaments/{apartament_id}")
async def update_apartaments(
    session: AsyncSessionDep,
    apartament_id: int,
    apartament_data: ApartmentUpdateSchema,
    user: User = Depends(current_active_user),
):
    try:
        return await ApartamentQueryBuilder.update_apartaments(
            session, apartament_id, apartament_data, user.id
        )
    except UnauthorizedAccess as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ApartamentsNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
