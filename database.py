from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base

engine = create_engine(
    "sqlite:///./roam.db",
    connect_args={"check_same_thread": False},  # needed for SQLite + FastAPI
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def init_db():
    """Create tables if they don't exist yet. Called once on app startup."""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
