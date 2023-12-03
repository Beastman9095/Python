import interactions

class EditEmbed(interactions.Extension):
    
    @interactions.message_context_menu(name="Edit Embed")
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
        
        embed_notes = modal_ctx.responses["notes"] if modal_ctx.responses["notes"] else None
        
        announcement_embed = interactions.Embed(title=modal_ctx.responses["title"], 
                                                description=modal_ctx.responses["description"],
                                                color=ctx.author.top_role.color if ctx.guild else None)
        
        announcement_embed.set_author(name=ctx.author.user.tag, icon_url=ctx.author.display_avatar.url)
        announcement_embed.set_footer(text=f"{ctx.client.footer} ? {ctx.author.id}")
        announcement_embed.set_image(url=ctx.target.embeds[0].image.url if ctx.target.embeds[0].image else None)
            
        if embed_notes:
            announcement_embed.add_field(name="Notes:", value=embed_notes)
            
        await modal_ctx.edit(ctx.target, embed=announcement_embed)