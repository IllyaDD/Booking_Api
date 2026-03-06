from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    name: str
    surname: str


class UserCreate(schemas.BaseUserCreate):
    name: str
    surname: str


class UserUpdate(schemas.BaseUserUpdate):
    name: Optional[str] = None
    surname: Optional[str] = None
