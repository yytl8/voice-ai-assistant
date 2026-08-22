from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from ..settings import settings

class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.database_url, pool_pre_ping=True, pool_recycle=1800)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with SessionLocal() as session:
        yield session
