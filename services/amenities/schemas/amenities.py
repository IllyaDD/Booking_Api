from sqlmodel import SQLModel
from typing import Optional, List


class AmenitiesResponseSchema(SQLModel):
    id: int
    name: str


class AmenitiesCreateSchema(SQLModel):
    name: str


class AmenitiesUpdateSchemas(SQLModel):
    name: Optional[str]


class AmenitiesListResponseSchema(SQLModel):
    items: List[AmenitiesResponseSchema]
