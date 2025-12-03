from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os

# In your .env, set:
# DATABASE_URL=postgresql+asyncpg://user:password@db:5432/app_db
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    Usage example in your routes:

        from fastapi import Depends
        from sqlalchemy.ext.asyncio import AsyncSession

        @app.get("/users")
        async def list_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with SessionLocal() as session:
        yield session
