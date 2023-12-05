import interactions
import uuid
from common.models import EMBEDDED_MESSAGE
import datetime
from common.consts import METADATA


class Suggestion(interactions.Extension):
    def __init__(self, bot: interactions.Client):
        self.set_extension_error(self.error_handler)
        
    @interactions.slash_command(description="Suggest something to the server.",
                                scopes=METADATA["guilds"])
    async def suggest(self, ctx: interactions.SlashContext):
        
        SUGGESTION_ID = str(uuid.uuid4())
            
        suggestion_modal = interactions.Modal(
            interactions.ShortText(label="Title", 
                                   placeholder="Suggestion title", 
                                   custom_id="title"),
            interactions.ParagraphText(label="Description", 
                                       placeholder="Suggestion details", 
                                       custom_id="description"),
            title="Create a Suggestion",
            custom_id=f"suggestion?{SUGGESTION_ID}",
        )
        
        emojis = ["👍", "👎"]
        
        await EMBEDDED_MESSAGE(uuid=SUGGESTION_ID,
                               counts={emoji: 0 for emoji in emojis},
                               user_ids={},
                               created_at=datetime.datetime.utcnow(),
                               author_id=str(ctx.author.id),
                               attachment="None",
                               ).create()
            
        # Move to ext.listeners.modal_worker.py to move along
        await ctx.send_modal(modal=suggestion_modal)
        
    async def error_handler(self, error: Exception, ctx: interactions.BaseContext, *args, **kwargs):
        match error.status:
            case 404:
                await ctx.send(f"Interaction timed out.", ephemeral=True)
                return
                
        raise(error)