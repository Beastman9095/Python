import interactions

import os
import asyncio
import logging
import dotenv
import aiohttp

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from interactions.ext import prefixed_commands


from common.models import EMBEDDED_MESSAGE
from common.utils.formatter import CustomFormatter
from common.consts import *

dotenv.load_dotenv(".env")


logger = logging.getLogger("zeutium_core_bot")
logger.setLevel(logging.DEBUG)

stderr_handler = logging.StreamHandler()
# Change to logging.DEBUG to see debug messages
stderr_handler.setLevel(logging.WARNING)
stderr_handler.setFormatter(CustomFormatter())
logger.addHandler(stderr_handler)

file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(CustomFormatter())
logger.addHandler(file_handler)


activity = interactions.Activity.create(name="on play.zeutium.com",
                                        type=interactions.ActivityType.PLAYING)

intents = interactions.Intents.DEFAULT


class DiscordClient(interactions.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.footer = METADATA["footer"]

        self.sync_interactions = True
        self.disable_dm_commands = False
        self.send_command_tracebacks = False
        self.send_not_ready_messages = True
        self.delete_unused_application_cmds = True

        self.intents = intents
        self.logger = logger
        self._activity = activity

    @interactions.listen()
    async def on_ready(self):
        await self.change_presence(interactions.Status.IDLE, self._activity)
        print(f'Logged on as {self.user}!')


client = DiscordClient()

prefixed_commands.setup(client)


async def start():
    mongo_client = AsyncIOMotorClient(os.environ["MONGO_URI"],
                                      server_api=ServerApi("1"))

    await init_beanie(mongo_client.zeutium_core_bot,
                      document_models=[EMBEDDED_MESSAGE]) 

    client.session = aiohttp.ClientSession()

    for root, _, files in os.walk("ext"):
        for file in files:
            if file.endswith('.py'):
                client.load_extension(os.path.join(root, file)[:-3].replace('/', '.').replace('\\', '.'))

    try:
        await client.astart(os.environ["TOKEN"])
    finally:
        await client.session.close()

            
if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        logger.info("Shutting down.")
