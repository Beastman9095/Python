import interactions
from common.utils.attachment import Attachment
import uuid
from common.models import EMBEDDED_MESSAGE
import datetime

"""
This extension integrates a slash command to create announcements.

__Purpose:__ Receive the \"announce\" application command context from the user and process it. Following this 
it responds to the user with a modal to create the announcement desired. If an attachment has been chosen,
it is saved locally to ./attachments/ and the filename is stored in the EMBEDDED_MESSAGE as `attachment`.
In the case of a mention input, it is stored in the modal custom_id as `mention.id` which is later used to
fetch either the role oobject or the user object.

__Utilizes:__ modal_worker.py && component_worker.py
"""


class Announce(interactions.Extension):
    
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
        
        # Unique identifier for the announcement on the database
        # Stored in embed footer as well for easy access
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
        
        # Attachment needs to be specified as "None" due to library limitations, it was either that or a blank string
        await EMBEDDED_MESSAGE(uuid=ANNOUNCEMENT_ID,
                               counts={emoji: 0 for emoji in emojis},
                               user_ids={},
                               created_at=datetime.datetime.utcnow(),
                               author_id=str(ctx.author.id),
                               attachment=attachment.filename if attachment else "None",
                               ).create()
        
        if attachment:
            await Attachment().save(attachment.url, attachment.filename)
            
        """
        After the modal is sent the actions take place in the following order:
        ext.listeners.modal_worker.py -> ext.listeners.component_worker.py
        """
        await ctx.send_modal(modal=announcement_modal)
