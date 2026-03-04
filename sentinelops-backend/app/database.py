"""
SentinelOps Database Configuration
Author: Arsh Verma

Supports both SQLite (default, for local dev) and PostgreSQL (production).
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# SQLite needs special connect_args to allow multi-threaded access
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def create_tables():
    # Import models locally to avoid circular import with Base and models
    from app import models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
