"""
Alembic environment configuration for async SQLAlchemy - Farmers Marketplace.

TODO: Contributors should import models as they implement them.
This template provides the basic async setup for PostgreSQL migrations.

"""
import asyncio
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

from app.core.config import get_settings
from app.models.base import Base
from app.models.users.user import User  # noqa: F401

# Import notification models
from app.models.shared.notification import (  # noqa: F401
    Notification,
    NotificationTemplate,
    UserNotificationPreference,
    DeviceToken,
)

# TODO: Import all models here as they are implemented to ensure they are registered with SQLAlchemy
# Examples:
# from app.models import Farmer, Product, Order, Location  # noqa


# Contributors should add imports when implementing models following CONTRIBUTING.md issues

# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy URL from environment
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async support."""
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section) or {},
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online()) 