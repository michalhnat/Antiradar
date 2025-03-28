import logging
from asyncio import Queue
from typing import Optional, cast

from fbchat_muqit import Client, Message, ThreadType

logger = logging.getLogger("app.services.AsyncRunner")


class MessengerClient(Client):
    _process_queue: Optional[Queue]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._process_queue = None

    @classmethod
    async def startSession(
        cls,
        session_cookies: Optional[str] = None,
        process_queue: Optional[Queue] = None,
    ):
        if session_cookies is None:
            raise ValueError(
                "session_cookies must be provided as a string path"
            )

        client = cls()
        client = await super().startSession(cookies_file_path=session_cookies)
        logging.info("Starting MessengerClient session")

        client._process_queue = process_queue  # type: ignore
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
            if self._process_queue:
                await self._process_queue.put(message)


# async def main():
#     cookies_path = "backend/cred/ufc-facebook.json"
#     bot = await MessengerClient.startSession(cookies_path)
#     if await bot.isLoggedIn():
#         fetch_client_info = await bot.fetchUserInfo(bot.uid)
#         client_info = fetch_client_info[bot.uid]
#         logger.info(f"Logged in as {client_info.name}")
#     try:
#         await bot.listen()
#     except Exception as e:
#         logger.error(f"Error: {e}")


# if __name__ == "__main__":
#     asyncio.run(main())
