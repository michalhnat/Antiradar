import logging
from typing import Dict, Optional

from backend.app.db.models import Location
from geoalchemy2.elements import WKTElement
from geopy.geocoders import Nominatim
from backend.app.db.models import Location


class RecordCreator:
    def __init__(
        self, agent: ParseAgent, general_location: str, db_session=None
    ):
        self.agent = agent
        self.geolocator = Nominatim(user_agent="Antiradar")
        self.general_location = general_location
        self.db_session = db_session

    def _parse_msg(self, message: str) -> Optional[Dict]:
        try:
            parsed = self.agent.parse_message(message)
            return parsed
        except Exception as e:
            logging.error(f"Error parsing message: {e}")
            return None

    def _geocode(self, town: str, street: str) -> Optional[object]:
        try:
            address = (
                f"{town} {street} {self.general_location}"
                if town and street
                else town or street
            )
            if not address:
                return None

            print(address)
            coordinates = self.geolocator.geocode(address)
            return coordinates
        except Exception as e:
            print(f"Error geocoding address: {e}")
            return None

    def create_record(self, message: str) -> Optional[Dict]:
        try:
            location_data = self._parse_msg(message)
            if not location_data:
                return None

            town = location_data.get("town", "")
            street = location_data.get("street", "")

            coordinates = self._geocode(town, street)

            result = {
                "town": town,
                "street": street,
                "latitude": None,
                "longitude": None,
            }

            if coordinates:
                result.update(
                    {
                        "latitude": coordinates.latitude,
                        "longitude": coordinates.longitude,
                    }
                )

            point = None
            if location_data.get("latitude") and location_data.get(
                "longitude"
            ):
                point = WKTElement(
                    f"POINT({location_data['longitude']} {location_data['latitude']})",
                    srid=4326,
                )

            location = Location(
                town=location_data.get("town", ""),
                street=location_data.get("street", ""),
                lat=location_data.get("latitude"),
                long=location_data.get("longitude"),
                geom=point,
            )

            return result
        except Exception as e:
            logging.error(f"Error creating address: {e}")
            return None
