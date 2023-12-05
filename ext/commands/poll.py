import interactions
import uuid
from common.utils.consts import METADATA


class Numbers():
    def __init__(self):
        self.numbers = METADATA["numbers"]


class Poll(interactions.Extension):
    def __init__(self, bot: interactions.Client):
        self.set_extension_error(self.error_handler)
        self.numbers = Numbers().numbers

    @interactions.slash_command(description="Create a poll for the server", scopes=[METADATA["guild"]])
    @interactions.slash_option(
        name="description",
        description="A description for the poll",
        required=False,
        opt_type=interactions.OptionType.STRING
    )
    @interactions.slash_option(
        name="mention",
        description="Mention a user or a role!",
        required=False,
        opt_type=interactions.OptionType.MENTIONABLE
    )
    async def poll(self, ctx: interactions.SlashContext, description: str = None, mention=None):
        POLL_ID = str(uuid.uuid4())
        
        poll_modal = interactions.Modal(
            interactions.ShortText(label="Title",
                                   placeholder="Here comes the poll title.",
                                   custom_id="title"),
            interactions.ParagraphText(label="Options",
                                       placeholder="Input your options here, each starting with \"-\", for eg.\n-Option1\n-Option2\n.\n.\n.",
                                       custom_id="options"),
            title="Create a Poll",
            custom_id=f"poll?{POLL_ID}",
        )
        
        await ctx.send_modal(modal=poll_modal)

    async def error_handler(self, error: Exception, ctx: interactions.BaseContext, *args, **kwargs):
        match error.status:
            case 404:
                await ctx.send(f"Interaction timed out.", ephemeral=True)
                return

        raise (error)
