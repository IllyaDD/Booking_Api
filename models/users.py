from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import VARCHAR, Column, DateTime
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from fastapi_users_db_sqlmodel import SQLModelBaseUserDB

if TYPE_CHECKING:
    from .apartaments import Apartment
    from .booking import Booking
    from .ratings import Rating


class User(SQLModelBaseUserDB, table=True):
    __tablename__ = "users"
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(VARCHAR(250), nullable=False))
    surname: str = Field(sa_column=Column(VARCHAR(250), nullable=False))
    description: Optional[str] = Field(sa_column=Column(VARCHAR(255), nullable=True))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    )

    # Relationships
    apartments: List["Apartment"] = Relationship(back_populates="owner")
    bookings: List["Booking"] = Relationship(back_populates="guest")
    ratings: List["Rating"] = Relationship(back_populates="user")
