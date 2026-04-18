from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.sql.selectable import SelectState
from sqlmodel import select
from models import Apartment, apartaments, ratings
from models.apartaments import ApartmentType
from services.apartaments.errors import (
    ApartamentsNotFound,
    ApartamentAlreadyExists,
    InvalidFilters,
)
from dependency.session import AsyncSessionDep
from services.apartaments.schemas import (
    ApartmentListResponseSchema,
    ApartmentShortResponseSchema,
    ApartmentUpdateSchema,
)
from services.apartaments.schemas.apartaments import (
    ApartmentCreateSchema,
    ApartmentResponseSchema,
)
from common.errors import UnauthorizedAccess


class ApartamentQueryBuilder:
    @staticmethod
    async def get_apartament_by_id(
        session: AsyncSessionDep, apartament_id: int
    ) -> ApartmentResponseSchema:
        query = (
            select(Apartment)
            .where(Apartment.id == apartament_id)
            .options(selectinload(Apartment.amenities), selectinload(Apartment.ratings))
        )
        result = await session.execute(query)
        apartament = result.scalar_one_or_none()
        if apartament is None:
            raise ApartamentsNotFound(apartament_id)

        return ApartmentResponseSchema(
            **apartament.model_dump(),
            amenities=apartament.amenities,
            ratings=apartament.ratings_avg,
        )

    @staticmethod
    async def create_apartament(
        session: AsyncSessionDep, user_id: int, apartament_data: ApartmentCreateSchema
    ) -> ApartmentResponseSchema:
        apartament_dict = apartament_data.model_dump()
        apartament_dict["owner_id"] = user_id

        apartament = Apartment(**apartament_dict)
        session.add(apartament)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ApartamentAlreadyExists(apartament_data.name)
        await session.refresh(apartament)
        await session.refresh(apartament, attribute_names=["amenities", "ratings"])

        return ApartmentResponseSchema(
            **apartament.model_dump(),
            amenities=apartament.amenities,
            ratings=apartament.ratings_avg,
        )

    @staticmethod
    async def delete_apartament(session: AsyncSessionDep, user_id, apartament_id: int):
        apartament = await ApartamentQueryBuilder.check_apartament_owner(
            session, user_id, apartament_id
        )
        await session.delete(apartament)
        await session.commit()

    @staticmethod
    async def check_apartament_owner(
        session: AsyncSessionDep, user_id: int, apartament_id: int
    ):
        query = select(Apartment).where(Apartment.id == apartament_id)
        result = await session.execute(query)
        apartment = result.scalar_one_or_none()
        if not apartment:
            raise ApartamentsNotFound(apartament_id)
        if apartment.owner_id != user_id:
            raise UnauthorizedAccess
        return apartment

    @staticmethod
    async def update_apartaments(
        session: AsyncSessionDep,
        apartament_id: int,
        apartament_data: ApartmentUpdateSchema,
        user_id: int,
    ):
        apartament = await ApartamentQueryBuilder.check_apartament_owner(
            session, user_id, apartament_id
        )
        for key, value in apartament_data.model_dump(exclude_unset=True).items():
            setattr(apartament, key, value)
        await session.commit()
        await session.refresh(apartament)
        return apartament

    @staticmethod
    async def get_apartaments(
        session: AsyncSessionDep,
        name: Optional[str] = None,
        type: Optional[ApartmentType] = None,
        min_rooms: Optional[int] = None,
        max_rooms: Optional[int] = None,
        min_guests: Optional[int] = None,
        max_guests: Optional[int] = None,
    ) -> Page[ApartmentShortResponseSchema]:
        if min_rooms is not None and max_rooms is not None and min_rooms > max_rooms:
            raise InvalidFilters("min_rooms cannot be greater than max_rooms")
        if (
            min_guests is not None
            and max_guests is not None
            and min_guests > max_guests
        ):
            raise InvalidFilters("min_guests cannot be greater than max_guests")

        query = select(Apartment).options(selectinload(Apartment.ratings))

        if name is not None:
            query = query.where(Apartment.name.ilike(f"%{name}%"))
        if type is not None:
            query = query.where(Apartment.type == type)
        if min_rooms is not None:
            query = query.where(Apartment.rooms >= min_rooms)
        if max_rooms is not None:
            query = query.where(Apartment.rooms <= max_rooms)
        if min_guests is not None:
            query = query.where(Apartment.max_guests >= min_guests)
        if max_guests is not None:
            query = query.where(Apartment.max_guests <= max_guests)

        def transformer(items: List[Apartment]) -> List[ApartmentShortResponseSchema]:
            return [
                ApartmentShortResponseSchema(
                    id=item.id,
                    name=item.name,
                    type=item.type,
                    ratings=item.ratings_avg,
                )
                for item in items
            ]

        return await paginate(session, query, transformer=transformer)
