import os, time
from typing import Generator
from sqlalchemy import Column, Integer, String, Text, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://app_user:app_password@postgres-db:5432/app_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(max_retries: int = 15, delay_seconds: float = 2.0) -> None:
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries}: initializing DB...")
            Base.metadata.create_all(bind=engine)
            print("Database tables initialized")
            return
        except OperationalError as e:
            print(f"DB not ready yet: {e}")
            if attempt == max_retries:
                raise
            time.sleep(delay_seconds)

def check_connection() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
