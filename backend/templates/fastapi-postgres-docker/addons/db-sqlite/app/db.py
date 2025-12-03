from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os

# In your .env, set:
# DATABASE_URL=sqlite+aiosqlite:///./app.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session for SQLite.

    TODO:
    - Import and use this in your routes when you add real DB logic.
    """
    async with SessionLocal() as session:
        yield session
