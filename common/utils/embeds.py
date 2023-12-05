import interactions
from ext.commands.poll import Numbers


class Modal_Response_Embed(interactions.Embed):
    def __init__(self, ctx: interactions.ModalContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = ctx.responses["title"]
        self.color = ctx.author.top_role.color if ctx.guild else None

    def set_author_from_ctx(self, ctx):
        self.set_author(name=ctx.author.user.tag if ctx.guild else ctx.author.tag,
                        icon_url=ctx.author.display_avatar.url)
        return
