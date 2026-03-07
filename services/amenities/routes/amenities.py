from dependency.session import AsyncSessionDep
from models import User
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_filters import FilterValues
from fastapi_pagination import Page
from services.amenities.schemas.amenities import (
    AmenitiesCreateSchema,
    AmenitiesResponseSchema,
    AmenitiesUpdateSchemas,
    AmenityFilters,
)
from services.amenities.query_builder import AmenitiesQueryBuider
from services.amenities.errors import AmenityNotFound, AmenityAlreadyExists
from services.users.modules.manager import current_superuser

amenities_router = APIRouter()


@amenities_router.post(
    "/amenities",
    status_code=status.HTTP_201_CREATED,
    response_model=AmenitiesResponseSchema,
)
async def create_amenities(
    amenities_data: AmenitiesCreateSchema, session: AsyncSessionDep
):
    try:
        new_amenity = await AmenitiesQueryBuider.create_amenities(
            session, amenities_data=amenities_data
        )
    except AmenityAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return AmenitiesResponseSchema.model_validate(new_amenity)


@amenities_router.get("/amenities/{amenity_id}", response_model=AmenitiesResponseSchema)
async def get_amenitites_by_id(amenity_id: int, session: AsyncSessionDep):
    try:
        return await AmenitiesQueryBuider.get_amenities_by_id(session, amenity_id)
    except AmenityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@amenities_router.delete(
    "/amenities/{amenity_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_amenity(
    amenity_id: int, session: AsyncSessionDep, user: User = Depends(current_superuser)
):
    try:
        await AmenitiesQueryBuider.delete_aminity(session, amenity_id)
    except AmenityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@amenities_router.patch("/amenities/{amenity_id}")
async def update_amenity(
    session: AsyncSessionDep, amenity_id: int, data: AmenitiesUpdateSchemas
):
    try:
        return await AmenitiesQueryBuider.update_amenity(session, amenity_id, data)
    except AmenityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@amenities_router.get("/amenities/", response_model=Page[AmenitiesResponseSchema])
async def get_amenities(
    session: AsyncSessionDep,
    filters: FilterValues = Depends(AmenityFilters),
):
    return await AmenitiesQueryBuider.get_amenities(session, filters)
