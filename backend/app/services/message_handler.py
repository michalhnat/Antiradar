import os

from record_creator import RecordCreator
from dotenv import load_dotenv
from parase_agent import ParseAgent
from geoalchemy2.elements import WKTElement

load_dotenv()

API_KEY = os.environ.get("OPEN_ROUTER_API")

system_prompt = """You are an AI assistant specializing in extracting and formatting location information from unstructured text messages. Your task is to identify and structure any mentioned towns, districts, and streets, while assuming Zielona Góra as the default location unless another town is explicitly stated.

Formatting Rules:
Structure: Extracted locations should be formatted as a JSON object with the following keys:
- "town": The town or district name.
- "street": The street name (if available).

Default Location: If no town is specified, assume Zielona Góra.

Recognizing Districts: Identify known districts such as Łężyca, Droszków, Gronów, Ochla, Świdnica, Nowogród Bobrzański and format them appropriately.

Contextual Clues: Consider landmarks or directional hints (e.g., "naprzeciwko Pieprzyka," "za nexterio w stronie ZG") to determine the correct location.

No Extra Elements: Do not add numbers, bullet points, or unnecessary text—just return the formatted JSON object.

Ignore Irrelevant Messages: If a message lacks meaningful location data, do not return anything.

Examples:
Input:
"Spotkajmy się na ulicy Zjednoczenia."

Output:
{"town": "Zielona Góra", "street": "Zjednoczenia"}

Input:
"Jestem w Łężycy, blisko Poziomkowej."

Output:
{"town": "Łężyca", "street": "Poziomkowa"}

Input:
"Przyjeżdżaj do Wilkanowa!"

Output:
{"town": "Wilkanowo", "street": ""}

Input:
"Idziemy na rynek?"

Output:
{}
"""
general_location = "Zielona Góra, Lubuskie, Poland"

agent = ParseAgent(
    open_router_api_key=API_KEY,
    system_prompt=system_prompt,
    model="google/gemma-3-27b-it:free",
)

record_creator = RecordCreator(agent, general_location)


class MessageHandler:
    def __init__(self, record_creator, db_session=None):
        self.record_creator = record_creator
        self.db_session = db_session

    def process_message(self, message_text):
        location_data = self.record_creator.create_address(message_text)

        if (
            location_data
            and self.db_session
            and location_data.get("town")
            or location_data.get("street")
        ):
            from app.db.models import (
                Location,
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

            self.db_session.add(location)
            self.db_session.commit()

            location_data["id"] = location.id

        return location_data
