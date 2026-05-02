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
    rooms: int = Field(ge=1)
    max_guests: int = Field(ge=1)
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApartmentUpdateSchema(SQLModel):
    name: Optional[str] = None
    address: Optional[str] = None
    type: Optional[ApartmentType] = None
    rooms: Optional[int] = Field(default=None, ge=1)
    max_guests: Optional[int] = Field(default=None, ge=1)
    description: Optional[str] = None
