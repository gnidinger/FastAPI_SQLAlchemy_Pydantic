from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

DATABASE_URL = "postgresql+asyncpg://postgres:rjslrjsl333@localhost:5432/postgres"

engine = create_async_engine(DATABASE_URL, echo=True)

# 비동기 세션을 위한 설정
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

Base: DeclarativeMeta = declarative_base()


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
