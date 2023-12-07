import interactions
import uuid
from common.consts import METADATA

"""
This extension integrates a slash command to create polls.

__Purpose:__ Receive the \"poll\" application command context from the user and process it. Following this 
it responds to the user with a modal to create the poll desired. All options are checked for a valid format
using the regex pattern within the modal_worker.py file and processed into the EMBEDDED_MESSAGE document there.

__Utilizes__: modal_worker.py && component_worker.py
"""


class Numbers():
    def __init__(self):
        self.numbers: list = METADATA["numbers"]
        
    def get_index(self, emoji):
        return self.numbers.index(emoji)
    

class Poll(interactions.Extension):
    def __init__(self, bot: interactions.Client):
        self.numbers: list = Numbers().numbers
        
        self.set_extension_error(self.error_handler)

    @interactions.slash_command(description="Create a poll for the server",
                                scopes=METADATA["guilds"])
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
        
        # Unique identifier for the poll on the database
        # Stored in embed footer as well for easy access
        POLL_ID = str(uuid.uuid4())
        
        poll_modal = interactions.Modal(
            interactions.ShortText(label="Title",
                                   placeholder="Here comes the poll title.",
                                   custom_id="title"),
            interactions.ParagraphText(label="Options",
                                       placeholder="Input your options here, each starting with \"-\", "
                                                   "for eg.\n-Option1\n-Option2\n.\n.\n.",
                                       custom_id="options"),
            title="Create a Poll",
            custom_id=f"poll?{POLL_ID}",
        )
        
        # EMBEDDED_MESSAGE documents of polls are created in the modal_worker as the options are dynamic
        
        """
        After the modal is sent the actions take place in the following order:
        ext.listeners.modal_worker.py -> ext.listeners.component_worker.py
        """
        await ctx.send_modal(modal=poll_modal)

    async def error_handler(self, error: Exception, ctx: interactions.BaseContext, *args, **kwargs):
        match error.status:
            case 404:
                await ctx.send(f"Interaction timed out.", ephemeral=True)
                return

        raise (error)
