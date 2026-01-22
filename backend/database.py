from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo = True
)

# Create SessionMaker
SessionLocal = sessionmaker(
    bind = engine,
    autocommit = False,
    autoflush = False
)

# DeclarativeBase for sqlalchemy models
Base  = declarative_base()

# Generator for session dependency injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
