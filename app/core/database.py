from typing import Generator
import logging

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with connection pool settings
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,  # Test connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    connect_args={"connect_timeout": 10}  # Connection timeout of 10 seconds
)

# Add event listeners for connection debugging
@event.listens_for(Engine, "connect")
def connect(dbapi_connection, connection_record):
    logger.debug("Database connection established")

@event.listens_for(Engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    logger.debug("Database connection checked out")

@event.listens_for(Engine, "checkin")
def checkin(dbapi_connection, connection_record):
    logger.debug("Database connection checked in")

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


# Dependency to get DB session
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
