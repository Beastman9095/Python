import importlib
import re
from contextlib import suppress

import interactions as ipy
from interactions.ext import prefixed_commands as prefixed

from common.consts import METADATA

import common.utils as utils


"""
This extension is used to synchronize the application commands and context menus with the Discord API.
"""


async def is_owner(ctx: ipy.BaseContext) -> bool:
    return ctx.user.id == METADATA["owner"]


class Sync(ipy.Extension):
    def __init__(self, client: ipy.Client):
        self.client = client

    @prefixed.prefixed_command()
    @ipy.check(is_owner)
    async def sync(self, ctx: prefixed.PrefixedContext):
        await self.client.synchronise_interactions(delete_commands=True)
        await ctx.reply(":white_check_mark: Synchronized commands.")


def setup(client: ipy.Client):
    Sync(client)