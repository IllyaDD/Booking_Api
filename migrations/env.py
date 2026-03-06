import sqlmodel
import asyncio
from logging.config import fileConfig
from pydantic import computed_field
from sqlalchemy import pool
from sqlalchemy.engine import URL, Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from sqlmodel import SQLModel
from common.settings import DatabaseConnectionSettings
from models import (
    User,
    Booking,
    Amenity,
    Apartment,
    ApartmentAmenityLink,
    ApartmentType,
    Rating,
)


class DatabaseMigrationSettings(DatabaseConnectionSettings):
    @computed_field
    @property
    def url(self) -> URL:
        return self.database.get_url()


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = DatabaseMigrationSettings().url.render_as_string(hide_password=False)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    conn_config = DatabaseMigrationSettings()
    engine = create_async_engine(
        url=conn_config.url,
        poolclass=pool.NullPool,
        echo=conn_config.database.debug,
        echo_pool="debug" if conn_config.database.debug else None,
    )
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())  # ← asyncio був не імпортований


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
