from sqlmodel import SQLModel
from typing import Optional, List
from fastapi_filters import create_filters_from_model, FilterValues


class AmenitiesResponseSchema(SQLModel):
    id: int
    name: str


class AmenitiesCreateSchema(SQLModel):
    name: str


class AmenitiesUpdateSchemas(SQLModel):
    name: Optional[str]


class AmenitiesListResponseSchema(SQLModel):
    items: List[AmenitiesResponseSchema]


AmenityFilters = create_filters_from_model(AmenitiesResponseSchema, include=["name"])
