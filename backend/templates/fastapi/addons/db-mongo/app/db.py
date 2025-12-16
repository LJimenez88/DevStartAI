# app/db_mongo.py

from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import os

#URI and DBname information has to be in env file.
#This was left here as a fall back so you will need to update this on your end
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "app_db")

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URI)
    return _client


async def get_db() -> AsyncGenerator:
    """
    Dependency you can inject into routes:

    async def my_route(db = Depends(get_db)):
        await db["items"].insert_one(...)
    """
    client = get_client()
    db = client[MONGO_DB_NAME]
    try:
        yield db
    finally:
        # We usually keep the client global, so nothing here.
        ...
