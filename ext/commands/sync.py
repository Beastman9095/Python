import interactions
from interactions.ext import prefixed_commands as prefixed

from common.consts import METADATA


"""
This extension is used to synchronize the application commands and context menus with the Discord API.
"""


async def is_owner(ctx: interactions.BaseContext) -> bool:
    return ctx.user.id == METADATA["owner"]


class Sync(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client = client

    @prefixed.prefixed_command()
    @interactions.check(is_owner)
    async def sync(self, ctx: prefixed.PrefixedContext):
        await self.client.synchronise_interactions(scopes=[guild.id for guild in self.client.guilds], delete_commands=True)
        await ctx.reply(":white_check_mark: Synchronized commands.")


def setup(client: interactions.Client):
    Sync(client)