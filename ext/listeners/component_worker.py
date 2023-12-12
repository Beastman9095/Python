from enum import Enum

import interactions

from ext.commands.poll import Numbers
from common.models import EMBEDDED_MESSAGE
import datetime

from interactions.api.events import Component


# Allows to differentiate between the three types of embedded messages
class ChoiceOption(Enum):
    ANNOUNCEMENT = "announcement"
    SUGGESTION = "suggestion"
    POLL = "poll"


# Puts the x/sum ratio in symbols format
def percentage_showcase_in_symbols(percentage_in_numbers):
    percentage_in_symbols = ""
    for _ in range(percentage_in_numbers):
        percentage_in_symbols += "█"
    for _ in range(10 - percentage_in_numbers):
        percentage_in_symbols += "░"
    return percentage_in_symbols


class ChoiceButton(interactions.Extension):
    def __init__(self, client: interactions.Client):

        self.ctx: interactions.ComponentContext
        self.client: interactions.Client = client
        self.message_uuid: str
        self.options_of_message = []

    @interactions.listen(Component)
    async def on_component(self, event: Component):
        self.ctx = event.ctx
        
        match self.ctx.custom_id.split("?")[0]:
            case "announcement":
                await self.callback_for_embedded_message_modals(ChoiceOption.ANNOUNCEMENT)
                return
            case "suggestion":
                await self.callback_for_embedded_message_modals(ChoiceOption.SUGGESTION)
                return
            case "poll":
                await self.callback_for_embedded_message_modals(ChoiceOption.POLL)
                return


    async def callback_for_embedded_message_modals(self, option):
        
        # Get the message unique identifier we have input from the custom_id
        self.message_uuid = self.ctx.component.custom_id.split("?")[1]

        embedded_message_document = await EMBEDDED_MESSAGE.find_one(EMBEDDED_MESSAGE.uuid == self.message_uuid)
    
        user_id = str(self.ctx.user.id)

        self.options_of_message = [child for component_row in self.ctx.message.components for child in component_row.components]

        embedded_message_document = await EMBEDDED_MESSAGE(
            uuid=self.message_uuid,
            author_id=user_id,
            counts={
                **{option.emoji.name: 0 for option in self.options_of_message},
            },
            user_ids={},
            created_at=datetime.datetime.now(),
            attachment="None",
        ).create() if not embedded_message_document else embedded_message_document

        selected_button = next((child 
                                for child in self.options_of_message 
                                if embedded_message_document.user_ids.get(user_id, None) == child.emoji.name), 
                               None)
        
        if selected_button:
            embedded_message_document.counts[selected_button.emoji.name] -= 1
        embedded_message_document.counts[self.ctx.component.emoji.name] += 1
        embedded_message_document.user_ids[user_id] = self.ctx.component.emoji.name

        await embedded_message_document.save()

        if option == ChoiceOption.POLL:
            await self.handle_poll_option(embedded_message_document, self.options_of_message)
        else:
            component_custom_id = "{}?{}".format(self.ctx.component.custom_id.split("?")[0],
                                                 self.ctx.component.custom_id.split("?")[1])
            
            components = interactions.spread_to_rows(*[interactions.Button(
                                                                        emoji=emoji, 
                                                                        label=embedded_message_document.counts.get(emoji), 
                                                                        style=interactions.ButtonStyle.GRAY, 
                                                                        custom_id=f"{component_custom_id}?{emoji}") 
                    for emoji in embedded_message_document.counts.keys()])
            
            await self.ctx.edit_origin(components=components)
        
        
    async def handle_poll_option(self, embedded_message_document, options_of_message):
        for option in options_of_message:
            emoji = option.emoji.name
            vote_count_of_emoji = embedded_message_document.counts[emoji]
            
            percentage_in_symbols = percentage_showcase_in_symbols(
                round((int(vote_count_of_emoji) / sum(embedded_message_document.counts.values())) * 10))

            self.ctx.message.embeds[0].fields[
                Numbers().get_index(emoji)].value = f"{percentage_in_symbols} ({vote_count_of_emoji} votes)"
            
        await self.ctx.edit_origin(embed=self.ctx.message.embeds[0],
                                   components=self.ctx.message.components)
