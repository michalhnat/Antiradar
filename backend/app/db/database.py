import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

logger = logging.getLogger(__name__)

Base = declarative_base()

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)

SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
