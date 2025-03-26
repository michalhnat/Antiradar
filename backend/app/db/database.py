from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import DATABASE_URL
import logging

engine = create_engine(DATABASE_URL)

SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    try:
        session = SessionMaker()
        return session
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
