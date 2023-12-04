from enum import Enum

import interactions

from ext.commands.poll import Numbers
from common.utils.models import EMBEDDED_MESSAGE
import datetime
from beanie import PydanticObjectId


class ChoiceOption(Enum):
    ANNOUNCEMENT = "announcement"
    SUGGESTION = "suggestion"
    POLL = "poll"


async def poll_get_vote_count_from_emoji(emoji, embed):
    field_index = [(Numbers().numbers.index(k)) for k in Numbers().numbers if k == emoji][0]
    button_field = embed.fields[field_index]
    vote_count_for_emoji = button_field.value.split("(")[1].split(" ")[0]
    return vote_count_for_emoji


def percentage_showcase(percentage):
    percentage_in_symbols = ""
    for i in range(percentage):
        percentage_in_symbols += "█"
    for i in range(10 - percentage):
        percentage_in_symbols += "░"
    return percentage_in_symbols


class SelectedButton(interactions.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ChoiceButton:
    def __init__(self, ctx):
        self.ctx = ctx
        self.client = self.ctx.client
        self.message_uuid = None
        self.filter_get_doc = {"_id": ctx.component.custom_id.split("?")[1]}
        self.options_of_message = []

    async def callback(self, option):
        self.message_uuid = self.ctx.component.custom_id.split("?")[1]

        message_object_on_db = await EMBEDDED_MESSAGE.find_one(EMBEDDED_MESSAGE.uuid == self.message_uuid)

        selected_button = None
        for component_row in self.ctx.message.components:
            for child in component_row.components:
                self.options_of_message.append(child.emoji.name)
                if message_object_on_db:
                    if message_object_on_db.user_ids.get(str(self.ctx.user.id)) == child.emoji.name:
                        selected_button = child
                        selected_row_index = self.ctx.message.components.index(component_row)
                        selected_button_index = component_row.components.index(child)

        if not message_object_on_db:
            message_object_on_db = await EMBEDDED_MESSAGE(
                uuid=self.message_uuid,
                author_id=str(self.ctx.author.id),
                counts={
                    **{option: 0 for option in self.options_of_message},
                },
                user_ids={},
                created_at=datetime.datetime.now(),
            ).create()

        if selected_button:
            message_object_on_db.counts[selected_button.emoji.name] -= 1
        message_object_on_db.counts[self.ctx.component.emoji.name] += 1
        message_object_on_db.user_ids[str(self.ctx.user.id)] = self.ctx.component.emoji.name

        await message_object_on_db.save()

        if option == ChoiceOption.POLL:
            for emoji in self.options_of_message:
                vote_count_of_emoji = message_object_on_db.counts[emoji]
                field_index = [(Numbers().numbers.index(k)) for k in Numbers().numbers if k == emoji][0]
                percentage_in_symbols = percentage_showcase(
                    round((int(vote_count_of_emoji) / sum(message_object_on_db.counts.values())) * 10))
                self.ctx.message.embeds[0].fields[
                    field_index].value = f"{percentage_in_symbols} ({vote_count_of_emoji} votes)"
            await self.ctx.edit_origin(embed=self.ctx.message.embeds[0],
                                       components=self.ctx.message.components)
            return
        else:
            if selected_button:
                self.ctx.message.components[selected_row_index].components[selected_button_index].label = \
                message_object_on_db.counts[selected_button.emoji.name]
            self.ctx.component.label = message_object_on_db.counts[self.ctx.component.emoji.name]

        await self.ctx.edit_origin(components=self.ctx.message.components)
