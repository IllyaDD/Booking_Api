from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import VARCHAR, Column

from .apartaments import ApartmentAmenityLink

if TYPE_CHECKING:
    from .apartaments import Apartment


class Amenity(SQLModel, table=True):
    __tablename__ = "amenities"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(VARCHAR(100), nullable=False, unique=True))

    # Relationships
    apartments: List["Apartment"] = Relationship(
        back_populates="amenities", link_model=ApartmentAmenityLink
    )
