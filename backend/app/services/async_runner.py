import asyncio
import logging
from asyncio import Queue

from backend.app.db.database import get_db_async
from backend.app.db.database_handler import DatabaseHandler
from backend.app.services.messenger_client import MessengerClient
from backend.app.services.parser import Parser
from backend.app.services.record_creator import RecordCreator

from backend.app.core.config import settings

OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY.get_secret_value()
COOKIES_PATH = settings.COOKIES_PATH
MODEL = settings.MODEL
SYSTEM_PROMPT = settings.SYSTEM_PROMPT
GENERAL_LOCATION = settings.GENERAL_LOCATION

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set")

if not COOKIES_PATH:
    raise ValueError("COOKIES_PATH is not set")

if not SYSTEM_PROMPT:
    raise ValueError("SYSTEM_PROMPT is not set")

if not GENERAL_LOCATION:
    raise ValueError("GENERAL_LOCATION is not set")

logger = logging.getLogger(__name__)

parser = Parser(
    open_router_api_key=OPENROUTER_API_KEY,
    system_prompt=SYSTEM_PROMPT,
    model=MODEL,
)

message_queue = Queue()

record_creator = RecordCreator(parser, GENERAL_LOCATION)
database_connector = DatabaseHandler()


async def run_listener():
    logger.info("Starting listener")

    bot = await MessengerClient.startSession(
        COOKIES_PATH, process_queue=message_queue
    )

    logger.info("Starting listener")
    if await bot.isLoggedIn():
        fetch_client_info = await bot.fetchUserInfo(bot.uid)
        client_info = fetch_client_info[bot.uid]
        logger.info("Logged in as %s", client_info.name)
    try:
        await bot.listen()

    except Exception as e:
        logger.error("Error: %s", e)


async def message_handler():
    while True:
        message = await message_queue.get()
        try:
            record = record_creator.create_record(message)
            if record:
                logger.info("Creating record: %s", record)

                db_session_gen = get_db_async()
                db_session = next(db_session_gen)
                try:
                    database_connector.add_location(db_session, record)
                except Exception as e:
                    logger.error("Database error: %s", e)
                finally:
                    try:
                        next(db_session_gen)
                    except StopIteration:
                        logger.info("Database session closed")
                    except Exception as e:
                        logger.error("Error closing database session: %s", e)
            else:
                logger.error("Error creating record")
        except Exception as e:
            logger.error("Error processing message: %s", e)


async def main():
    listener_task = asyncio.create_task(run_listener())
    handler_task = asyncio.create_task(message_handler())

    try:
        await asyncio.gather(
            listener_task, handler_task, return_exceptions=True
        )
    except Exception as e:
        logger.error("Error in main execution: %s", e)
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
