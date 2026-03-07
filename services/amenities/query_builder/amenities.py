from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from fastapi_filters import FilterValues
from fastapi_filters.ext.sqlalchemy import apply_filters
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from models import Amenity
from dependency.session import AsyncSessionDep
from services.amenities.errors import AmenityNotFound, AmenityAlreadyExists
from services.amenities.schemas import (
    AmenitiesCreateSchema,
    AmenitiesResponseSchema,
    AmenitiesUpdateSchemas,
)


class AmenitiesQueryBuider:
    @staticmethod
    async def create_amenities(
        session: AsyncSessionDep, amenities_data: AmenitiesCreateSchema
    ) -> AmenitiesResponseSchema:
        amenities_dict = amenities_data.model_dump()
        amenity = Amenity(**amenities_dict)
        session.add(amenity)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise AmenityAlreadyExists(amenities_data.name)
        await session.refresh(amenity)
        return amenity

    @staticmethod
    async def get_amenities_by_id(session: AsyncSessionDep, amenity_id: int) -> Amenity:
        query = select(Amenity).where(Amenity.id == amenity_id)
        result = await session.execute(query)
        amenity = result.scalar_one_or_none()
        if amenity is None:
            raise AmenityNotFound(amenity_id)
        return amenity

    @staticmethod
    async def delete_aminity(
        session: AsyncSessionDep,
        amenity_id: int,
    ) -> None:
        amenity = await AmenitiesQueryBuider.get_amenities_by_id(session, amenity_id)
        await session.delete(amenity)
        await session.commit()

    @staticmethod
    async def update_amenity(
        session: AsyncSessionDep, amenity_id: int, amenity_data: AmenitiesUpdateSchemas
    ):
        amenity = await AmenitiesQueryBuider.get_amenities_by_id(session, amenity_id)
        for key, value in amenity_data.model_dump(exclude_unset=True).items():
            setattr(amenity, key, value)
        await session.commit()
        await session.refresh(amenity)
        return amenity

    @staticmethod
    async def get_amenities(
        session: AsyncSessionDep, filters: FilterValues
    ) -> Page[Amenity]:
        query = select(Amenity)
        query = apply_filters(query, filters)
        return await paginate(session, query)
