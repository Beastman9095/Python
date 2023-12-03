import interactions
from enum import Enum
from extensions.commands.poll import Numbers

class ChoiceOption(Enum):
    ANNOUNCEMENT = "announcement"
    SUGGESTION = "suggestion"
    POLL = "poll"

class ChoiceButton():
    def __init__(self, ctx):
        self.ctx = ctx
        self.client = self.ctx.client
        self.message_uuid = None
        self.filter_get_doc = {"_id": ctx.component.custom_id.split("?")[1]}
        
        doc = self.client.mongodb_collection.find_one(self.filter_get_doc)
        if not doc:
            self.client.mongodb_collection.insert_one({**self.filter_get_doc})
            
    def PERCENTAGE_SHOWCASE(self, PERCENTAGE):
        PERCENTAGE_SHOWCASE = ""
        for i in range(PERCENTAGE):
            PERCENTAGE_SHOWCASE += "█"
        for i in range(10 - PERCENTAGE):
            PERCENTAGE_SHOWCASE += "░"
        return PERCENTAGE_SHOWCASE
            
    async def poll_get_vote_count_from_emoji(self, emoji, embed):
        field_index = [ (Numbers().numbers.index(k)) for k in Numbers().numbers if k == emoji][0]
        button_field = embed.fields[field_index]
        vote_count_for_emoji = button_field.value.split("(")[1].split(" ")[0]
        return vote_count_for_emoji
        
    async def callback(self, option):
        
        self.message_uuid = self.ctx.component.custom_id.split("?")[1]
        
        embed = self.ctx.message.embeds[0]
        
        doc = self.client.mongodb_collection.find_one(
            {
                "_id": self.message_uuid,
                f"user_ids.{self.ctx.user.id}": {"$exists": True},
            }
        )
        
        if doc:
            selected_emoji = doc["user_ids"][f"{self.ctx.user.id}"]
            
            i = 0
            sum = 0
            for component_row in self.ctx.message.components:
                for child in component_row.components:
                    try:
                        sum += int(doc["counts"][child.emoji.name])
                    except:
                        pass
                    if child.emoji.name == selected_emoji:
                        selected_button = child
                        if option == ChoiceOption.POLL:
                            other_emoji_vote_count = await self.poll_get_vote_count_from_emoji(selected_emoji, embed)
                            field_index = [ (Numbers().numbers.index(k)) for k in Numbers().numbers if k == selected_emoji][0]
                            other_emoji_vote_count = str(int(other_emoji_vote_count) - 1)
                            PERCENTAGE = self.PERCENTAGE_SHOWCASE(round((int(other_emoji_vote_count) / sum) * 10))
                            embed.fields[field_index].value = f"{PERCENTAGE} ({other_emoji_vote_count} votes)"
                        else:
                            selected_button.label = str(int(selected_button.label) - 1)
                            other_emoji_vote_count = selected_button.label
                        break
                    i += 1
                
            self.client.mongodb_collection.update_one(
                {"_id": self.message_uuid},
                {
                    "$unset": {f"user_ids.{self.ctx.user.id}": ""},
                    "$set": {f"counts.{selected_emoji}": other_emoji_vote_count},
                },
            )
        else:
            sum = 1
        
        if option == ChoiceOption.POLL:
            vote_count_for_emoji = await self.poll_get_vote_count_from_emoji(self.ctx.component.emoji.name, embed)
            field_index = [ (Numbers().numbers.index(k)) for k in Numbers().numbers if k == self.ctx.component.emoji.name][0]
            vote_count_for_emoji = str(int(vote_count_for_emoji) + 1)
            PERCENTAGE = self.PERCENTAGE_SHOWCASE(round((int(vote_count_for_emoji) / sum) * 10))
            embed.fields[field_index].value = f"{PERCENTAGE} ({vote_count_for_emoji} votes)"
        else:
            self.ctx.component.label = str(int(self.ctx.component.label) + 1)
            vote_count_for_emoji = self.ctx.component.label

        self.client.mongodb_collection.update_one(
            {
                "_id": self.message_uuid
            },
            {
                "$set":
                    {
                        f"counts.{self.ctx.component.emoji.name}": vote_count_for_emoji,
                        f"user_ids.{self.ctx.user.id}": self.ctx.component.emoji.name
                    }
            },
            upsert=True
        )
        if option == ChoiceOption.POLL:
            await self.ctx.edit_origin(embed=embed,
                                       components=self.ctx.message.components)
        else:
            await self.ctx.edit_origin(components=self.ctx.message.components)