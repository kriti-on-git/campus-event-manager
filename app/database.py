from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./campus.db"

# SQLite keeps things simple for the MVP.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


def get_db():
    """Provide a database session and clean up afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        # No orphaned connections on my watch.
        db.close()