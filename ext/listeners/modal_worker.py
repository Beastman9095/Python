import interactions
from common.models import EMBEDDED_MESSAGE
import uuid
from common.utils.attachment import Attachment
import datetime
import re
from ext.commands.poll import Numbers
from common.utils.embeds import Modal_Response_Embed


class ModalWorker(interactions.Extension):

    def __init__(self, _):
        self.numbers = Numbers().numbers

    @interactions.listen("modal_completion")
    async def modal_handling(self, event: interactions.events.ModalCompletion):
        ctx = event.ctx
        embed = Modal_Response_Embed(ctx, title=ctx.responses["title"],
                                     color=ctx.author.top_role.color if ctx.guild else None)

        embed.set_author_from_ctx(ctx)

        embed.set_footer(text=f"{ctx.client.footer} ? {uuid.uuid4()}")

        match ctx.custom_id.split("?")[0]:
            case "announcement":
                embed.description = ctx.responses["description"]

                if ctx.responses["notes"]:
                    embed.add_field(name="Notes:", value=ctx.responses["notes"])

                await self.receive_modal(ctx, embed)
                return
            case "suggestion":
                embed.description = ctx.responses["description"]

                await self.receive_modal(ctx, embed)
                return
            case "poll":
                await self.receive_modal(ctx, embed)
                return

    async def receive_modal(self, ctx: interactions.ModalContext, embed: interactions.Embed):

        modal_type = ctx.custom_id.split("?")[0]

        if not (
                embedded_message := await EMBEDDED_MESSAGE.find_one(
                    EMBEDDED_MESSAGE.uuid == ctx.custom_id.split("?")[1])):

            if not re.match("(-(.+)\n)+-(.+)", ctx.responses["options"]):
                await ctx.send("Invalid options provided. Please try again.", ephemeral=True)
                return

            user_inputs = [option[1:] for option in ctx.responses["options"].split("\n")]
            emojis = []

            for index, option in enumerate(user_inputs):
                embed.add_field(name=f"{self.numbers[index]} {option}", value="░░░░░░░░░░ (0 Votes)", inline=False)
                emojis.append(self.numbers[index])

            embedded_message = await EMBEDDED_MESSAGE(uuid=ctx.custom_id.split("?")[1],
                                                      counts={emoji: 0 for emoji in emojis},
                                                      user_ids={},
                                                      created_at=datetime.datetime.utcnow(),
                                                      author_id=str(ctx.author.id),
                                                      attachment="None",
                                                      ).create()

        file = None
        if embedded_message.attachment != "None":
            embed.set_image("attachment://" + embedded_message.attachment)
            file = await Attachment().get(embedded_message.attachment)

        store_components = []

        for emoji in embedded_message.counts.keys():
            store_components.append(
                interactions.Button(
                    style=interactions.ButtonStyle.GRAY if modal_type != "poll" else interactions.ButtonStyle.BLURPLE,
                    emoji=emoji,
                    label=embedded_message.counts[emoji] if modal_type != "poll" else None,
                    custom_id=f"{ctx.custom_id.split('?')[0]}?{ctx.custom_id.split('?')[1]}?{emoji}"
                )
            )

        components = interactions.spread_to_rows(
            *store_components
        )

        mention = None
        if len(ctx.custom_id.split("?")) == 3:
            mention_id = int(ctx.custom_id.split("?")[2])
            if member := await ctx.client.fetch_user(mention_id):
                mention = member.mention
            elif role := await ctx.guild.fetch_role(mention_id):
                mention = role.mention

        await ctx.send(content=mention,
                       embed=embed,
                       ephemeral=False,
                       file=file,
                       components=components)

        if file:
            await Attachment().delete(file)
