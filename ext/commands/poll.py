import interactions
import uuid
from common.utils.consts import METADATA
import re

"(\-(.+)\n)+-(.+)"


class Numbers():
    def __init__(self):
        self.numbers = METADATA["numbers"]


class Poll(interactions.Extension):
    def __init__(self, bot: interactions.Client):
        self.set_extension_error(self.error_handler)
        self.numbers = Numbers().numbers

    @interactions.slash_command(description="Create a poll for the server")
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
        poll_modal = interactions.Modal(
            interactions.ShortText(label="Title",
                                   placeholder="Here comes the poll title.",
                                   value="",
                                   custom_id="title"),

            interactions.ParagraphText(label="Options",
                                       placeholder="Input your options here, each starting with \"-\", for eg.\n-Option1\n-Option2\n.\n.\n.",
                                       value="",
                                       custom_id="options"),
            title="Create a Poll",
            custom_id="poll_modal",
        )
        await ctx.send_modal(modal=poll_modal)

        modal_ctx: interactions.ModalContext = await ctx.bot.wait_for_modal(poll_modal)

        poll_embed = interactions.Embed(title=modal_ctx.responses["title"],
                                        description=description,
                                        color=ctx.author.top_role.color if ctx.guild else None)
        
        if not re.match("(\-(.+)\n)+-(.+)", modal_ctx.responses["options"]):
            await modal_ctx.send("Invalid options provided. Please try again.", ephemeral=True)
            return 

        poll_embed.set_author(name=ctx.author.user.tag if ctx.guild else ctx.author.tag,
                              icon_url=ctx.author.display_avatar.url)
        poll_embed.set_footer(text=f"{ctx.client.footer} ? {uuid.uuid4()}")

        user_inputs = [option[1:] for option in modal_ctx.responses["options"].split("\n")]

        for index, option in enumerate(user_inputs):
            poll_embed.add_field(name=f"{self.numbers[index]} {option}", value="░░░░░░░░░░ (0 Votes)", inline=False)
            user_inputs[index] = interactions.Button(
                style=interactions.ButtonStyle.BLURPLE,
                emoji=self.numbers[index],
                custom_id="poll?{}?{}".format(poll_embed.footer.text.split("?")[1].replace(" ", ""),
                                              self.numbers[index])
            )

        components: list[interactions.ActionRow] = interactions.spread_to_rows(
            *user_inputs
        )

        await modal_ctx.send(content=mention.mention if mention else None,
                             embed=poll_embed,
                             ephemeral=False,
                             components=components)

    async def error_handler(self, error: Exception, ctx: interactions.BaseContext, *args, **kwargs):
        match error.status:
            case 404:
                await ctx.send(f"Interaction timed out.", ephemeral=True)
                return

        raise (error)
