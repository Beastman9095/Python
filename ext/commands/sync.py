import interactions
from common.utils.consts import METADATA
from interactions.ext import prefixed_commands as prefixed

def owner_check(ctx: prefixed.PrefixedContext):
    return ctx.author.id == METADATA["owner"]

class EditEmbed(interactions.Extension):
    
    @prefixed.prefixed_command()
    @interactions.check(owner_check)
    async def sync(self, ctx: prefixed.PrefixedContext):
        await self.bot.synchronise_interactions(scopes=[METADATA["guild"], 0], delete_commands=True)
        await ctx.reply(":white_check_mark: Synchronized commands.")
