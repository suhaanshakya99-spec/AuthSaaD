from sqlalchemy.ext.asyncio import (create_async_engine, async_sessionmaker, AsyncSession)
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


POSTGRESQL_URL = settings.POSTGRESQL_URL
engine = create_async_engine(url=POSTGRESQL_URL)

LocalSession = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass
