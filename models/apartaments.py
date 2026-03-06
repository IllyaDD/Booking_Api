from enum import StrEnum
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import VARCHAR, Column, Integer, DateTime
from sqlalchemy.types import Enum as SAEnum
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .users import User
    from .booking import Booking
    from .amenities import Amenity
    from .ratings import Rating


class ApartmentType(StrEnum):
    FLAT = "flat"
    HOUSE = "house"


class ApartmentAmenityLink(SQLModel, table=True):
    __tablename__ = "apartment_amenity"

    apartment_id: Optional[int] = Field(
        default=None, foreign_key="apartments.id", primary_key=True
    )
    amenity_id: Optional[int] = Field(
        default=None, foreign_key="amenities.id", primary_key=True
    )


class Apartment(SQLModel, table=True):
    __tablename__ = "apartments"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(VARCHAR(255), nullable=False))
    address: str = Field(sa_column=Column(VARCHAR(255), nullable=False))
    type: ApartmentType = Field(
        sa_column=Column(SAEnum(ApartmentType), nullable=False)
    )
    rooms: int = Field(sa_column=Column(Integer, nullable=False, default=1))
    max_guests: int = Field(sa_column=Column(Integer, nullable=False, default=1))
    description: Optional[str] = Field(
        sa_column=Column(VARCHAR(1000), nullable=True)
    )
    owner_id: int = Field(nullable=False, foreign_key="users.id")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    )

    # Relationships
    owner: Optional["User"] = Relationship(back_populates="apartments")
    bookings: List["Booking"] = Relationship(back_populates="apartment")
    amenities: List["Amenity"] = Relationship(
        back_populates="apartments", link_model=ApartmentAmenityLink
    )
    ratings: List["Rating"] = Relationship(back_populates="apartment")
