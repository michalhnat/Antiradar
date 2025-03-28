import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import DATABASE_URL

# Create logger
logger = logging.getLogger(__name__)

# Create the declarative base that models will inherit from
Base = declarative_base()

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)

SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# def init_db():
#     try:
#         from backend.app.db.models import (
#             Location,
#         )

#         logger.info("Creating database tables")
#         Base.metadata.create_all(bind=engine)
#         logger.info("Database tables created successfully")
#     except Exception as e:
#         logger.error(f"Failed to create database tables: {e}", exc_info=True)
#         raise


def get_db_async():
    try:
        session = SessionMaker()
        yield session
    finally:
        session.close()
