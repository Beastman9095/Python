from common.utils.choice_components import ChoiceButton, ChoiceOption

from interactions.api.events import Component
import interactions

import os
import asyncio
import logging

import aiohttp
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from common.utils.models import SINGLE_CHOICE_COMPONENT

from common.utils.consts import *
import dotenv

dotenv.load_dotenv()


logger = logging.getLogger("zeutium_core_bot")
logger.setLevel(logging.DEBUG)

stderr_handler = logging.StreamHandler()
stderr_handler.setLevel(logging.WARNING)
logger.addHandler(stderr_handler)

file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a")
file_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)


activity = interactions.Activity.create(name="on play.zeutium.com",
                                        type=interactions.ActivityType.PLAYING)

intents = interactions.Intents.new(
    guilds=True,
    guild_members=True,
    guild_moderation=True,
    guild_messages=True,
    direct_messages=True,
    message_content=True,
)


class DiscordClient(interactions.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.footer = METADATA["footer"]
        self.debug_scope = METADATA["guild"]

        self.disable_dm_commands = False
        self.send_command_tracebacks = False
        self.fetch_members = True
        self.sync_interactions = True

        self.intents = intents
        self.logger = logger
        self._activity = activity

    @interactions.listen()
    async def on_ready(self):
        await self.change_presence(interactions.Status.IDLE, self._activity)
        print(f'Logged on as {self.user}!')


client = DiscordClient()


async def start():
    mongo_client = AsyncIOMotorClient(os.environ["MONGO_URI"],
                                      server_api=ServerApi("1"))

    await init_beanie(mongo_client.Zeutium,
                      document_models=[SINGLE_CHOICE_COMPONENT]) 

    client.session = aiohttp.ClientSession()

    for root, dirs, files in os.walk("ext"):
        for file in files:
            if file.endswith('.py'):
                client.load_extension(os.path.join(root, file)[:-3].replace('/', '.').replace('\\', '.'))

    try:
        await client.astart(os.environ["TOKEN"])
    finally:
        await client.session.close()


@interactions.listen(Component)
async def on_component(event: Component):
    ctx = event.ctx
    match ctx.custom_id.split("?")[0]:
        case "announcement":
            await ChoiceButton(ctx).callback(ChoiceOption.ANNOUNCEMENT)
            return
        case "suggestion":
            await ChoiceButton(ctx).callback(ChoiceOption.SUGGESTION)
            return
        case "poll":
            await ChoiceButton(ctx).callback(ChoiceOption.POLL)
            return
    pass
            
if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        logger.info("Shutting down.")
