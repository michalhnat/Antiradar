from typing import Generator

from sqlalchemy.orm import Session

from backend.app.db.database import SessionMaker


def get_db() -> Generator[Session, None, None]:
    db = SessionMaker()
    try:
        yield db
    finally:
        db.close()
