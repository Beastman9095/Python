import interactions
from common.utils.attachment import Attachment
import os
import uuid


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
        
        file = None
        if attachment:
            await Attachment(attachment).save()
            file = interactions.File(f"./attachments/{attachment.filename}")
            
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
            custom_id="announcement_modal",
        )
        await ctx.send_modal(modal=announcement_modal)
            
        modal_ctx: interactions.ModalContext = await ctx.bot.wait_for_modal(announcement_modal)
        
        announcement_embed: interactions.Embed = interactions.Embed(title=modal_ctx.responses["title"], 
                                                description=modal_ctx.responses["description"],
                                                color=ctx.author.top_role.color if ctx.guild else None)
        
        announcement_embed.set_author(name=ctx.author.user.tag if ctx.guild else ctx.author.tag,
                                      icon_url=ctx.author.display_avatar.url)
        announcement_embed.set_footer(text=f"{ctx.client.footer} ? {uuid.uuid4()}")
        announcement_embed.set_image(url=f"attachment://{attachment.filename}" if attachment else None)
            
        if modal_ctx.responses["notes"]:
            announcement_embed.add_field(name="Notes:", value=modal_ctx.responses["notes"])
            
        components = interactions.spread_to_rows(
            interactions.Button(
                style=interactions.ButtonStyle.GRAY,
                emoji="🎉",
                label="0",
                custom_id="announcement?{}?🎉".format(announcement_embed.footer.text.split("?")[1].replace(" ", ""))
            ),
            interactions.Button(
                style=interactions.ButtonStyle.GRAY,
                emoji="❤️",
                label="0",
                custom_id="announcement?{}?❤️".format(announcement_embed.footer.text.split("?")[1].replace(" ", ""))
            )
        )

        await modal_ctx.send(embed=announcement_embed,
                             content=mention.mention if mention else None,
                             ephemeral=False,
                             files=file,
                             components=components)
        if attachment:
            os.remove("./attachments/" + attachment.filename)
