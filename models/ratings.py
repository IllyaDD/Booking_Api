from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, DateTime, Integer, VARCHAR
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .users import User
    from .apartaments import Apartment


class Rating(SQLModel, table=True):
    __tablename__ = "ratings"

    id: Optional[int] = Field(default=None, primary_key=True)
    apartment_id: int = Field(nullable=False, foreign_key="apartments.id")
    user_id: int = Field(nullable=False, foreign_key="users.id")
    score: int = Field(sa_column=Column(Integer, nullable=False))  # 1–5
    comment: Optional[str] = Field(sa_column=Column(VARCHAR(1000), nullable=True))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    )

    # Relationships
    apartment: Optional["Apartment"] = Relationship(back_populates="ratings")
    user: Optional["User"] = Relationship(back_populates="ratings")
