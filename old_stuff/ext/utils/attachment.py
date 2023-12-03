import aiohttp
import io
import tempfile
from PIL import Image

class Attachment():
    def __init__(self, attachment):
        self.attachment = attachment
    
    async def save(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.attachment.url) as response:
                image_data = Image.open(io.BytesIO(await response.read()))
                image_data.save(f"./attachments/{self.attachment.filename}")