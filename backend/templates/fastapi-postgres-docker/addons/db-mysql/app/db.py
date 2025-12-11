import os
import time
from typing import Generator

from sqlalchemy import create_engine, Column, Integer, String, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import OperationalError

# -------------------------------------------------------------------
# DATABASE_URL
# -------------------------------------------------------------------
# Example:
#   mysql+pymysql://app_user:app_password@mysql-db:3306/app_db
#
# In Docker, "mysql-db" will be the service name for MySQL.
# Locally you can use "localhost" instead.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://app_user:app_password@mysql-db:3306/app_db",
)

# SQLAlchemy setup (sync engine is fine for now)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# -------------------------------------------------------------------
# ORM model
# -------------------------------------------------------------------
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)


# -------------------------------------------------------------------
# Helpers for FastAPI dependencies
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(max_retries: int = 10, delay_seconds: float = 3.0) -> None:
    """
    Create DB tables, retrying a few times while the MySQL container boots.

    This prevents the API container from crashing if MySQL isn't ready yet.
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries}: initializing DB...")
            Base.metadata.create_all(bind=engine)
            print("✔ Database tables initialized")
            return
        except OperationalError as e:
            print(f"⚠️  DB not ready yet: {e}")
            if attempt == max_retries:
                print("❌ Giving up after max retries")
                raise
            time.sleep(delay_seconds)


def check_connection() -> None:
    """Used by /health-db if you ever want to check DB status."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
