from email import message
import os
import logging

import asyncio
from asyncio import Queue
from backend.app.services import DatabaseHandler
from backend.app.services.MessengerClient import MessengerClient
from backend.app.services.RecordCreator import RecordCreator
from dotenv import load_dotenv
from backend.app.services.Parser import Parser
from backend.app.services.DatabaseHandler import DatabaseHandler
from backend.app.db.database import get_db
from geoalchemy2.elements import WKTElement
from typing import Optional

load_dotenv()

API_KEY = os.environ.get("OPEN_ROUTER_API")
COOKIES = os.environ.get("COOKIES_PATH")

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

parser = Parser(
    open_router_api_key=API_KEY,
    system_prompt=system_prompt,
    model="google/gemma-3-27b-it:free",
)

message_queue = Queue()

record_creator = RecordCreator(parser, general_location)
database_connector = DatabaseHandler(get_db())
messenger_client = MessengerClient(proccess_queue=message_queue)


async def run_listener():
    bot = await MessengerClient.startSession(COOKIES)
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
    while True:
        message = await message_queue.get()
        record = record_creator.create_record(message)
        if record:
            database_connector.add("locations", record)
        else:
            logging.error("Error creating record")


async def main():
    try:
        asyncio.run(run_listener())
    except Exception as e:
        logging.error(f"Error: {e}")

    try:
        asyncio.run(message_handler())
    except Exception as e:
        logging.error(f"Error: {e}")
