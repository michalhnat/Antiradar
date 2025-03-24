from parase_agent import ParseAgent
from geopy.geocoders import Nominatim
from typing import Dict, Optional
import logging


class RecordCreator:
    def __init__(self, agent: ParseAgent, general_location: str):
        self.agent = agent
        self.geolocator = Nominatim(user_agent="Antiradar")
        self.general_location = general_location

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

    def create_address(self, message: str) -> Optional[Dict]:
        try: 
            location = self._parse_msg(message)
            town = location.get("town", "")
            street = location.get("street", "")

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

            return result
        except Exception as e:
            logging.error(f"Error creating address: {e}")
            return None
