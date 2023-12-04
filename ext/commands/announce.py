import interactions
from common.utils.attachment import Attachment
import os
import uuid
from common.utils.models import EMBEDDED_MESSAGE
import datetime


async def error_handler(error: Exception, ctx: interactions.BaseContext, mention=None, attachment=None, *args, **kwargs):
    match error.status:
        case 404:
            await ctx.send(f"Interaction timed out.", ephemeral=True)
            if attachment is not None:
                os.remove("./attachments/" + attachment.filename)
            return

    raise error


class Announce(interactions.Extension):
    
    def __init__(self, bot: interactions.Client):
        self.set_extension_error(error_handler)
    
    @interactions.slash_command(description="Announce something to the server!")
    @interactions.slash_option(
        name="mention",
        description="Mention a user or a role!",
        required=False,
        opt_type=interactions.OptionType.MENTIONABLE
    )     
    @interactions.slash_option(
        name="attachment",
        description="Add an image to your announcement",
        required=False,
        opt_type=interactions.OptionType.ATTACHMENT
    )
    async def announce(self, ctx: interactions.SlashContext, mention=None, attachment=None):
        
        ANNOUNCEMENT_ID = str(uuid.uuid4())
            
        announcement_modal = interactions.Modal(
            interactions.ShortText(label="Title", 
                                   placeholder="Announcement title", 
                                   custom_id="title"),
            interactions.ParagraphText(label="Description", 
                                       placeholder="Announcement details", 
                                       custom_id="description"),
            interactions.ShortText(label="Notes", 
                                   placeholder="Additional info (optional)", 
                                   custom_id="notes", 
                                   required=False),
            title="Create an Announcement",
            custom_id=f"announcement?{ANNOUNCEMENT_ID}",
        )
        
        if mention:
            announcement_modal.custom_id += f"?{mention.id}"
        
        emojis = ["🎉", "❤️"]
        
        await EMBEDDED_MESSAGE(uuid=ANNOUNCEMENT_ID,
                               counts={emoji: 0 for emoji in emojis},
                               user_ids={},
                               created_at=datetime.datetime.utcnow(),
                               author_id=str(ctx.author.id),
                               attachment=attachment.filename if attachment else "None",
                               ).create()
        
        if attachment:
            await Attachment().save(attachment)
            
        # Move to ext.listeners.modal_worker.py to move along
        await ctx.send_modal(modal=announcement_modal)
