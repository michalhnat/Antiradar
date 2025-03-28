import logging
from typing import List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db_async
from backend.app.db.models import Location


class DatabaseHandler:
    def __init__(self, db_session: Session = Depends(get_db_async)):
        self.db = db_session

    def get_all_locations(self) -> List[Location]:
        try:
            logging.info("Fetching all locations")
            return self.db.query(Location).all()
        except Exception as e:
            raise Exception(f"Error fetching locations: {e}")

    def add_location(self, location: Location) -> Location:
        try:
            logging.info("Adding new location")
            self.db.add(location)
            self.db.commit()
            self.db.refresh(location)
            return location
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error adding location: {e}")

    def close(self):
        self.db.close()
