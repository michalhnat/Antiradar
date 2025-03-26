from email import message
import os
import logging

import asyncio
from asyncio import Queue

from backend.app.db.DatabaseHandler import DatabaseHandler
from backend.app.services.MessengerClient import MessengerClient
from backend.app.services.RecordCreator import RecordCreator
from dotenv import load_dotenv
from backend.app.services.Parser import Parser
from backend.app.db.database import get_db
from geoalchemy2.elements import WKTElement
from typing import Optional

load_dotenv()

API_KEY = os.environ.get("OPEN_ROUTER_API")
COOKIES = "backend/ufc-facebook.json"

system_prompt = """You are an AI assistant specialized in extracting and formatting location information from unstructured text messages. Your task is to identify and structure any mentioned towns, districts, streets, and related geographic indicators. Follow these rules:

• Extraction:
  - Identify explicitly mentioned towns and districts.
  - Use "Zielona Góra" as the default town if no other is specified.
  - Recognize known city sourunding towns and districts:
        Towns: Babimost, Czerwieńsk, Kargowa, Nowogród Bobrzański, Sulechów. 
        Powiat Zielonogórski

        Rural communes: Bojadła, Świdnica, Trzebiechów, Zabór. 

        Districts and settlements of Zielona Góra: Barcikowice, Drzonków, Jany, Jarogniewice, Jeleniów, Kiełpin, Krępa, Łężyca, Ługowo, Marzęcin, Nowy Kisielin, Ochla, Przylep, Racula, Stary Kisielin, Sucha, Zatonie, Zawada. 

  - Look for additional geographic references like air towns or any location indications in texts mentioning "ZielonaGora" or "ZielonoGórski powiat" and include them as valid towns.

• Street Extraction:
  - Identify street names if present.
  - Incorporate contextual clues (e.g., additional descriptors like "Iveco" appended to a street name) into the street value.
  - Avoid extracting company or brand names as part of the geographic data.

• Formatting:
  - Output must be a JSON object with exactly two keys:
      • "town": the town or district name (or a valid location extracted, including air towns if applicable).
      • "street": the street name if available; otherwise, an empty string.
  - If no meaningful location information is present, return an empty JSON object {}.
  - Do not include any extra text, numbers, or formatting beyond the JSON object.

Examples:
- Input: "Spotkajmy się na ulicy Zjednoczenia."  
  Output: {"town": "Zielona Góra", "street": "Zjednoczenia"}

- Input: "Droszków ustawili się za dino w stronę Zg"  
  Output: {"town": "Droszków", "street": "Dino"}

- Input: "Przed iveco susza"  
  Output: {"town": "Zielona Góra", "street": "Iveco"}

- Input: "Wjazd do płot stoją."  
  Output: {"town": "Zielona Góra", "street": "Płoty"}

- Input: "Wojska Polskiego NBP"  
  Output: {"town": "Zielona Góra", "street": "Wojska Polskiego NBP"}

- Input: "Trasa Północna Bodzio Meble"  
  Output: {"town": "Zielona Góra", "street": "Trasa Północna Bodzio Meble"}

- Input: "Spotkajmy się na ulicy Zjednoczenia."
  Output: {"town": "Zielona Góra", "street": "Zjednoczenia"}
  
- Input: "Jestem w Łężycy, blisko Poziomkowej."
  Output: {"town": "Łężyca", "street": "Poziomkowa"}
  
- Input: "Przyjeżdżaj do Wilkanowa!"
  Output: {"town": "Wilkanowo", "street": ""}
  
- Input: "Idziemy na rynek?"
  Output:{}

- Input: Uwaga-suszsrka. Zatonie okolice kościoła w stronę ZG
  Output: {"town": "Zatonie", "street": "kościół"}

  I beg yu be precise so Nominatim geolocation will work the best


Ensure that any reference to air towns or geographical indicators within texts mentioning "ZIelonaGora" or "ZielonoGórski powiat" is treated as valid location data in the extraction.

"""
general_location = "Lubuskie, Poland"

parser = Parser(
    open_router_api_key=API_KEY,
    system_prompt=system_prompt,
    model="google/gemini-2.5-pro-exp-03-25:free",
)

message_queue = Queue()

record_creator = RecordCreator(parser, general_location)
database_connector = DatabaseHandler(get_db())


async def run_listener():
    bot = await MessengerClient.startSession(
        COOKIES, proccess_queue=message_queue
    )

    logging.info("Starting listener")
    if await bot.isLoggedIn():
        fetch_client_info = await bot.fetchUserInfo(bot.uid)
        client_info = fetch_client_info[bot.uid]
        logging.info(f"Logged in as {client_info.name}")
    try:
        await bot.listen()
    except Exception as e:
        logging.error(f"Error: {e}")
        await bot.stopSession()


async def message_handler():
    try:
        while True:
            message = await message_queue.get()
            record = record_creator.create_record(message)
            if record:
                try:
                    database_connector.add_location(record)
                except Exception as e:
                    logging.error(f"Database error: {e}")
            else:
                logging.error("Error creating record")
    finally:
        database_connector.close()


async def main():
    listener_task = asyncio.create_task(run_listener())
    handler_task = asyncio.create_task(message_handler())

    try:
        await asyncio.gather(listener_task, handler_task)
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        if not listener_task.done():
            listener_task.cancel()
        if not handler_task.done():
            handler_task.cancel()

        try:
            await listener_task
        except asyncio.CancelledError:
            pass
        try:
            await handler_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":

    asyncio.run(main())
