import logging
from typing import Dict, Optional
from venv import logger

from backend.app.services.parser import Parser
from geopy.geocoders import Nominatim

from backend.app.db.models import Location

logger = logging.getLogger(__name__)


class RecordCreator:
    def __init__(self, agent: Parser, general_location: str, db_session=None):
        self.agent = agent
        self.geolocator = Nominatim(user_agent="Antiradar")
        self.general_location = general_location
        self.db_session = db_session

    def _parse_msg(self, message: str) -> Optional[Dict]:
        try:
            parsed = self.agent.parse_message(message)
            return parsed
        except Exception as e:
            logger.error("Error parsing message: %s", e)
            return None

    def _geocode(self, town: str, street: str) -> Optional[object]:
        try:
            address = (
                f"{street} {town} {self.general_location}"
                if town and street
                else town or street
            )
            if not address:
                return None

            logger.info("Geocoding address: %s", address)

            coordinates = self.geolocator.geocode(address)
            logger.info("Geocoded address: %s", coordinates)
            return coordinates
        except Exception as e:
            logger.info("Error geocoding address: %s", e)
            return None

    def create_record(self, message: str) -> Optional[Location]:
        latitude = None
        longitude = None
        town = ""
        street = ""

        try:
            location_data = self._parse_msg(message)
            if not location_data:
                logger.warning("Failed to parse message: %s", message)
                return None

            town = location_data.get("town", "")
            street = location_data.get("street", "")

            coordinates = self._geocode(town, street)
            if coordinates:
                latitude = coordinates.latitude  # type: ignore
                longitude = coordinates.longitude  # type: ignore
            else:
                logger.warning(
                    f"Could not geocode: Town='{town}', Street='{street}'"
                )

            location = Location(
                town=town,
                street=street,
                lat=latitude,
                long=longitude,
                message=message,
            )
            return location

        except Exception as e:
            logger.error(
                "Error creating Location record: %s", e, exc_info=True
            )
            return None
