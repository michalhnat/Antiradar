from fbchat_muqit import Client, Message, ThreadType
import asyncio
import logging
from asyncio import Queue

logger = logging.getLogger("backend.app.services.AsyncRunner")


class MessengerClient(Client):
    def __init__(self, proccess_queue: Queue = None, **kwargs):
        super().__init__(**kwargs)
        self.proccess_queue = proccess_queue

    @classmethod
    async def startSession(cls, session_cookies=None, proccess_queue=None):
        # Override the startSession method to handle the proccess_queue parameter
        client = await super().startSession(session_cookies)
        client.proccess_queue = proccess_queue
        return client

    async def onMessage(
        self,
        mid,
        author_id: str,
        message_object: Message,
        thread_id,
        thread_type=ThreadType.USER,
        **kwargs,
    ):
        if author_id != self.uid:
            message = message_object.text
            logger.info(f"Received message: {message}")
            if self.proccess_queue:
                await self.proccess_queue.put(message)


async def main():
    cookies_path = "backend/ufc-facebook.json"
    bot = await MessengerClient.startSession(cookies_path)
    if await bot.isLoggedIn():
        fetch_client_info = await bot.fetchUserInfo(bot.uid)
        client_info = fetch_client_info[bot.uid]
        logger.info(f"Logged in as {client_info.name}")
    try:
        await bot.listen()
    except Exception as e:
        logger.error(f"Error: {e}")
        await bot.stopSession()


if __name__ == "__main__":
    asyncio.run(main())
