import logging
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.db.models import Location

logger = logging.getLogger(__name__)


class DatabaseHandler:
    def get_all_locations(self, db: Session) -> List[Location]:
        try:
            locations = db.query(Location).all()
            logger.info("Successfully fetched %d locations.", len(locations))
            return locations
        except SQLAlchemyError as e:
            logger.error("Database error fetching locations: %s", e)
            raise Exception(f"Database error fetching locations: {e}")
        except Exception as e:
            logger.error("Unexpected error fetching locations: %s", e)
            raise Exception(f"Unexpected error fetching locations: {e}")

    def add_location(self, db: Session, location: Location) -> Location:
        try:
            logger.info(
                "Attempting to add location to DB: Town=%s, Street=%s",
                location.town,
                location.street,
            )
            db.add(location)
            db.commit()
            db.refresh(location)
            logger.info("Successfully added location with ID: %s", location.id)
            return location
        except SQLAlchemyError as e:
            logger.error("Database error adding location: %s", e)
            db.rollback()
            raise Exception(f"Database error adding location: {e}")
        except Exception as e:
            logger.error("Unexpected error adding location: %s", e)
            db.rollback()
            raise Exception(f"Unexpected error adding location: {e}")

    def get_all_locations_in_last_x_hours(
        self, db: Session, x_hours: int
    ) -> List[Location]:
        try:
            locations = (
                db.query(Location)
                .filter(
                    Location.post_time
                    >= datetime.now() - timedelta(hours=x_hours)
                )
                .all()
            )
            logger.info(
                "Successfully fetched %d locations in the last %d hours.",
                len(locations),
                x_hours,
            )
            return locations
        except SQLAlchemyError as e:
            logger.error("Database error fetching locations: %s", e)
            raise Exception(f"Database error fetching locations: {e}")
        except Exception as e:
            logger.error("Unexpected error fetching locations: %s", e)
            raise Exception(f"Unexpected error fetching locations: {e}")

    def get_all_locations_since(
        self, db: Session, since: datetime
    ) -> List[Location]:
        try:
            locations = (
                db.query(Location).filter(Location.post_time >= since).all()
            )
            logger.info(
                "Successfully fetched %d locations since %s.",
                len(locations),
                since,
            )
            return locations
        except SQLAlchemyError as e:
            logger.error("Database error fetching locations: %s", e)
            raise Exception(f"Database error fetching locations: {e}")
        except Exception as e:
            logger.error("Unexpected error fetching locations: %s", e)
            raise Exception(f"Unexpected error fetching locations: {e}")
