from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from settings import settings

Base = declarative_base()
connect_args = {"check_same_thread": False}
pool = None

engine = create_async_engine(
    settings.db_url, connect_args=connect_args, poolclass=pool, echo=False
)
AsyncSQLiteSessionLocal = sessionmaker(  # type: ignore
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with AsyncSQLiteSessionLocal() as session:
        yield session


async def reset_sqlite_database() -> None:

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
