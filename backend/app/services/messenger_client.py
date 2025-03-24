
from fbchat_muqit import Client, Message, ThreadType
import asyncio
import logging

class MessengerClient(Client):

    async def onMessage(self, mid, author_id: str, message_object: Message, thread_id, thread_type=ThreadType.USER, **kwargs):
        if author_id != self.uid:
            # temp print
            print(message_object.text)


async def main():
    cookies_path = "path to json cookies"
    bot = await MessengerClient.startSession(cookies_path)
    if await bot.isLoggedIn():
        fetch_client_info = await bot.fetchUserInfo(bot.uid)
        client_info = fetch_client_info[bot.uid]
        logging.info(f"Logged in as {client_info.name}")
    try:
        await bot.listen()
    except Exception as e:
        logging.error(f"Error: {e}")
        await bot.stopSession()


asyncio.run(main()) 
