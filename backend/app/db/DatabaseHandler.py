import logging
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.db import models


class DatabaseHandler:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_locations(self) -> List[models.Location]:
        try:
            logging.info("Fetching all locations")
            return self.db.query(models.Location).all()
        except Exception as e:
            logging.error(f"Error fetching locations: {e}")
            raise

    def add_location(self, location: models.Location) -> models.Location:
        try:
            logging.info("Adding new location")
            self.db.add(location)
            self.db.commit()
            self.db.refresh(location)
            return location
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error adding location: {e}")
            raise

    def close(self):
        self.db.close()
