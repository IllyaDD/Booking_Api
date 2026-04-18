from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime

from models import ApartmentType
from services.amenities.schemas import AmenitiesResponseSchema


class ApartmentResponseSchema(SQLModel):
    id: int
    name: str
    address: str
    type: ApartmentType
    rooms: int
    max_guests: int
    description: str
    owner_id: int
    amenities: List[AmenitiesResponseSchema]
    created_at: datetime
    ratings: float


class ApartmentShortResponseSchema(SQLModel):
    id: int
    name: str
    type: ApartmentType
    ratings: float


class ApartmentListResponseSchema(SQLModel):
    items: List[ApartmentShortResponseSchema]


class ApartmentCreateSchema(SQLModel):
    name: str
    address: str
    type: ApartmentType
    rooms: int
    max_guests: int
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApartmentUpdateSchema(SQLModel):
    name: Optional[str]
    address: Optional[str]
    type: Optional[ApartmentType]
    rooms: Optional[int]
    max_guests: Optional[int]
    description: Optional[str]
