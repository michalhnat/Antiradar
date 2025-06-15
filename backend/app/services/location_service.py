import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.repositories.location import LocationRepository
from backend.app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationResponse,
)

logger = logging.getLogger(__name__)


class LocationService:
    def __init__(self, db: Session):
        self.repository = LocationRepository(db)

    def get_location(self, location_id: int) -> Optional[LocationResponse]:
        location = self.repository.get_by_id(location_id)
        return LocationResponse.model_validate(location) if location else None

    def get_locations(
        self, skip: int = 0, limit: int = 100
    ) -> List[LocationResponse]:
        locations = self.repository.get_all(skip=skip, limit=limit)
        return [
            LocationResponse.model_validate(location) for location in locations
        ]

    def get_locations_by_town(
        self, town: str, skip: int = 0, limit: int = 100
    ) -> List[LocationResponse]:
        locations = self.repository.get_by_town(town, skip=skip, limit=limit)
        return [
            LocationResponse.model_validate(location) for location in locations
        ]

    def get_recent_locations(self, hours: int) -> List[LocationResponse]:
        locations = self.repository.get_in_last_hours(hours)
        return [
            LocationResponse.model_validate(location) for location in locations
        ]

    def get_locations_since(self, since: datetime) -> List[LocationResponse]:
        locations = self.repository.get_since_datetime(since)
        return [
            LocationResponse.model_validate(location) for location in locations
        ]

    def create_location(
        self, location_data: LocationCreate
    ) -> LocationResponse:
        location = self.repository.create(location_data)
        return LocationResponse.model_validate(location)

    def update_location(
        self, location_id: int, location_data: LocationUpdate
    ) -> Optional[LocationResponse]:
        location = self.repository.update(location_id, location_data)
        return LocationResponse.model_validate(location) if location else None

    def delete_location(self, location_id: int) -> bool:
        return self.repository.delete(location_id)

    def get_location_count(self) -> int:
        return self.repository.count()
