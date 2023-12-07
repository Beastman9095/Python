import interactions


class ErrorWorker(interactions.Extension):
    @interactions.listen()
    async def on_error(self, event: interactions.api.events.Error):
        ctx: interactions.BaseContext = event.ctx
        error = event.error

        if ctx is None:
            raise error

        match error:
            case interactions.errors.HTTPException():
                match error.status:
                    case 400:
                        await ctx.send("An error occurred while processing your request.")
                    case 401:
                        await ctx.send("You're not authorized to do this.")
                    case 403:
                        await ctx.send("Interaction not found.")
                    case 404:
                        await ctx.send("Interaction not found.")
            case interactions.errors.CommandOnCooldown():
                await ctx.send("You're on cooldown. Try again later.")
            case AttributeError():
                await ctx.send("An error occurred while processing your request.")

