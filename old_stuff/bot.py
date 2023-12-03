from interactions import Client, Intents, listen
from interactions.api.events import Component
from ext.utils.choice_components import ChoiceButton, ChoiceOption
from pymongo import MongoClient
import os
import dotenv

dotenv.load_dotenv()


class DiscordClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._guilds = [int(os.getenv('GUILDS'))]
        self.footer = os.getenv('FOOTER')
        
        self.mongodb_client = MongoClient(os.getenv("MONGO_URI"))
        self.mongodb_db = self.mongodb_client[os.getenv("MONGO_DB")]
        self.mongodb_collection = self.mongodb_db[os.getenv("MONGO_COLLECTION")]
        
    @listen()
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        
client = DiscordClient(intents=Intents.DEFAULT)

@listen(Component)
async def on_component(event: Component):
    ctx = event.ctx
    match ctx.custom_id.split("?")[0]:
        case "announcement":
            await ChoiceButton(ctx).callback(ChoiceOption.ANNOUNCEMENT)
            return
        case "suggestion":
            await ChoiceButton(ctx).callback(ChoiceOption.SUGGESTION)
            return
        case "poll":
            await ChoiceButton(ctx).callback(ChoiceOption.POLL)
            return
    pass

for root, dirs, files in os.walk("extensions"):
    for file in files:
        if file.endswith('.py'):
            client.load_extension(os.path.join(root, file)[:-3].replace('/', '.'))
            
if __name__ == '__main__':
    client.start(os.getenv('TOKEN'))