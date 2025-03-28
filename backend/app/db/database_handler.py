import logging
from typing import List

from backend.app.db.database import get_db_async
from backend.app.db.models import Location

logger = logging.getLogger(__name__)


class DatabaseHandler:
    def __init__(self):
        self.db = next(get_db_async())

    def get_all_locations(self) -> List[Location]:
        try:
            logger.info("Fetching all locations")
            return self.db.query(Location).all()
        except Exception as e:
            raise Exception("Error fetching locations: %s", str(e))

    def add_location(self, location: Location) -> Location:
        try:
            logger.info("Adding new location")
            self.db.add(location)
            self.db.commit()
            self.db.refresh(location)
            return location
        except Exception as e:
            raise Exception("Error adding location: %s", str(e))

    def close(self):
        self.db.close()
