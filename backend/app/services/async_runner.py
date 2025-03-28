import asyncio
import logging
from asyncio import Queue

from backend.app.db.database_handler import DatabaseHandler
from backend.app.services.messenger_client import MessengerClient
from backend.app.services.parser import Parser
from backend.app.services.record_creator import RecordCreator

from backend.app.core.config import (
    COOKIES_PATH,
    GENERAL_LOCATION,
    MODEL,
    OPENROUTER_API_KEY,
    SYSTEM_PROMPT,
)
from backend.app.db.database import get_db_async

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set")

if not COOKIES_PATH:
    raise ValueError("COOKIES_PATH is not set")

if not SYSTEM_PROMPT:
    raise ValueError("SYSTEM_PROMPT is not set")

if not GENERAL_LOCATION:
    raise ValueError("GENERAL_LOCATION is not set")


parser = Parser(
    open_router_api_key=OPENROUTER_API_KEY,
    system_prompt=SYSTEM_PROMPT,
    model=MODEL,
)

message_queue = Queue()

record_creator = RecordCreator(parser, GENERAL_LOCATION)
database_connector = DatabaseHandler()


async def run_listener():
    logging.info("Starting listener")

    bot = await MessengerClient.startSession(
        COOKIES_PATH, process_queue=message_queue
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


async def message_handler():
    logging.info("Starting message handler")
    try:
        while True:
            message = await message_queue.get()
            record = record_creator.create_record(message)
            if record:
                logging.error(f"Creating record: {record}")
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
        await asyncio.gather(
            listener_task, handler_task, return_exceptions=True
        )
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
