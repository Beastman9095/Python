import interactions
import uuid

class Suggestion(interactions.Extension):
    def __init__(self, bot: interactions.Client):
        self.set_extension_error(self.error_handler)
        
    @interactions.slash_command(description="Suggest something to the server.")
    async def suggest(self, ctx: interactions.SlashContext):
        suggestion_modal = interactions.Modal(
            interactions.ShortText(label="Title", 
                                   placeholder="Here comes the announcement title.", 
                                   value="",
                                   custom_id="title"),
            
            interactions.ParagraphText(label="Description", 
                                       placeholder="Tell me about your announcement", 
                                       value="",
                                       custom_id="description"),
            title="Create a Suggestion",
            custom_id="suggestion_modal",
        )
        await ctx.send_modal(modal=suggestion_modal)
            
        modal_ctx: interactions.ModalContext = await ctx.bot.wait_for_modal(suggestion_modal)
        
        suggestion_embed = interactions.Embed(title=modal_ctx.responses["title"], 
                                                description=modal_ctx.responses["description"],
                                                color=ctx.author.top_role.color if ctx.guild else None)
        
        suggestion_embed.set_author(name=ctx.author.user.tag if ctx.guild else ctx.author.tag, 
                                    icon_url=ctx.author.display_avatar.url)
        suggestion_embed.set_footer(text=f"{ctx.client.footer} ? {uuid.uuid4()}")
            
        components: list[interactions.ActionRow] = interactions.spread_to_rows(
            interactions.Button(
                style=interactions.ButtonStyle.GRAY,
                emoji="👍",
                label="0",
                custom_id="suggestion?{}?👍".format(suggestion_embed.footer.text.split("?")[1].replace(" ", ""))
            ),
            interactions.Button(
                style=interactions.ButtonStyle.GRAY,
                emoji="👎",
                label="0",
                custom_id="suggestion?{}?👎".format(suggestion_embed.footer.text.split("?")[1].replace(" ", ""))
            )
        )

        await modal_ctx.send(embed=suggestion_embed,
                             ephemeral=False,
                             components=components)
        
    async def error_handler(self, error: Exception, ctx: interactions.BaseContext):
        match error.status:
            case 404:
                await ctx.send(f"Interaction timed out.", ephemeral=True)
                return
                
        raise(error)