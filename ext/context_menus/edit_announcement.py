import interactions
from common.consts import METADATA
from common.utils.embeds import Modal_Response_Embed


class EditAnnouncement(interactions.Extension):

    @interactions.message_context_menu(name="Edit Announcement",
                                       scopes=METADATA["guilds"])
    async def edit_embed(self, ctx: interactions.ContextMenuContext):
        edit_modal = interactions.Modal(
            interactions.ShortText(label="Title",
                                   placeholder="Here comes the announcement title.",
                                   value=ctx.target.embeds[0].title,
                                   custom_id="title"),

            interactions.ParagraphText(label="Description",
                                       placeholder="Tell me about your announcement",
                                       value=ctx.target.embeds[0].description,
                                       custom_id="description"),

            interactions.ShortText(label="Notes",
                                   placeholder="Anything else you'd like to add?",
                                   custom_id="notes",
                                   value=ctx.target.embeds[0].fields[0].value if ctx.target.embeds[0].fields else None,
                                   required=False),
            title="Edit an Announcement",
            custom_id="edit_modal",
        )
        await ctx.send_modal(modal=edit_modal)

        modal_ctx: interactions.ModalContext = await ctx.bot.wait_for_modal(edit_modal)

        edited_embed = Modal_Response_Embed(modal_ctx, title=modal_ctx.responses["title"],
                                            description=modal_ctx.responses["description"])

        edited_embed.set_footer(ctx.target.embeds[0].footer.text)

        if modal_ctx.responses["notes"]:
            edited_embed.add_field(name="Notes:", value=modal_ctx.responses["notes"])

        await modal_ctx.edit(ctx.target, embed=edited_embed, attachments=[])
