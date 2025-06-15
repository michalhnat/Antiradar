import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.db.models.models import Location
from backend.app.schemas.location import LocationCreate, LocationUpdate

logger = logging.getLogger(__name__)


class LocationRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, location_id: int) -> Optional[Location]:
        try:
            return (
                self.db.query(Location)
                .filter(Location.id == location_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(
                "Database error getting location by ID %s: %s", location_id, e
            )
            raise

    def get_by_town(
        self, town: str, skip: int = 0, limit: int = 100
    ) -> List[Location]:
        try:
            return (
                self.db.query(Location)
                .filter(Location.town.ilike(f"%{town}%"))
                .order_by(Location.post_time.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(
                "Database error fetching locations by town %s: %s", town, e
            )
            raise

    def get_in_last_hours(self, hours: int) -> List[Location]:
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            locations = (
                self.db.query(Location)
                .filter(Location.post_time >= cutoff_time)
                .order_by(Location.post_time.desc())
                .all()
            )
            logger.info(
                "Successfully fetched %d locations in the last %d hours.",
                len(locations),
                hours,
            )
            return locations
        except SQLAlchemyError as e:
            logger.error(
                "Database error fetching locations in last %d hours: %s",
                hours,
                e,
            )
            raise

    def get_since_datetime(self, since: datetime) -> List[Location]:
        try:
            locations = (
                self.db.query(Location)
                .filter(Location.post_time >= since)
                .order_by(Location.post_time.desc())
                .all()
            )
            logger.info(
                "Successfully fetched %d locations since %s.",
                len(locations),
                since,
            )
            return locations
        except SQLAlchemyError as e:
            logger.error(
                "Database error fetching locations since %s: %s", since, e
            )
            raise

    def create(self, location_data: LocationCreate) -> Location:
        try:
            db_location = Location(**location_data.model_dump())
            logger.info(
                "Attempting to add location to DB: Town=%s, Street=%s",
                db_location.town,
                db_location.street,
            )

            self.db.add(db_location)
            self.db.commit()
            self.db.refresh(db_location)

            logger.info(
                "Successfully added location with ID: %s", db_location.id
            )
            return db_location
        except SQLAlchemyError as e:
            logger.error("Database error adding location: %s", e)
            self.db.rollback()
            raise

    def update(
        self, location_id: int, location_data: LocationUpdate
    ) -> Optional[Location]:
        try:
            db_location = self.get_by_id(location_id)
            if not db_location:
                return None

            update_data = location_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_location, field, value)

            self.db.commit()
            self.db.refresh(db_location)
            logger.info(
                "Successfully updated location with ID: %s", location_id
            )
            return db_location
        except SQLAlchemyError as e:
            logger.error(
                "Database error updating location %s: %s", location_id, e
            )
            self.db.rollback()
            raise

    def delete(self, location_id: int) -> bool:
        try:
            db_location = self.get_by_id(location_id)
            if not db_location:
                return False

            self.db.delete(db_location)
            self.db.commit()
            logger.info(
                "Successfully deleted location with ID: %s", location_id
            )
            return True
        except SQLAlchemyError as e:
            logger.error(
                "Database error deleting location %s: %s", location_id, e
            )
            self.db.rollback()
            raise

    def count(self) -> int:
        try:
            return self.db.query(Location).count()
        except SQLAlchemyError as e:
            logger.error("Database error counting locations: %s", e)
            raise

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Location]:
        try:
            return (
                self.db.query(Location)
                .order_by(Location.post_time.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error("Database error fetching all locations: %s", e)
            raise
