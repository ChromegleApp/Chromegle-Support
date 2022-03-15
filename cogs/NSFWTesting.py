import base64
import io
import json
from typing import List

import aiohttp
import discord
from discord import Message
from discord.ext import commands

import config


class NSFWTesting(commands.Cog):

    def __int__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if message.channel.id != config.NSFWTesting.TEST_CHANNEL_ID:
            return

        if len(message.attachments) < 1:
            return

        images: List[discord.File] = []
        embeds: List[discord.Embed] = []

        await message.delete()

        async with aiohttp.ClientSession() as session:
            for attachment in message.attachments:
                async with session.get(attachment.url) as request:
                    image = await request.read()
                    buffer = io.BytesIO(image)
                    buffer.seek(0)

                    failed = True
                    if any(t in attachment.content_type for t in ["image/png"]):
                        async with session.post(
                                "https://chromegle.isaackogan.com/omegle/classify_image",
                                json={"base64": base64.b64encode(image).decode("utf-8")}
                        ) as _request:
                            try:
                                embeds.append(discord.Embed(
                                    title=f"Classified `{attachment.filename}`",
                                    description=f'```json\n{json.dumps((await _request.json())["payload"], indent=4)}```',
                                    colour=config.EMBED_COLOUR_INVIS
                                ))
                                failed = False
                            except:
                                pass
                    if failed:
                        embeds.append(discord.Embed(
                            title=f"Failed to Classify `{attachment.filename}`",
                            description=f"```json\n{json.dumps({'error': 'Unsupported file-type.', 'message': 'Try a standard PNG file.'}, indent=4)}```",
                            colour=config.EMBED_COLOUR_INVIS
                        ))

                    images.append(discord.File(buffer, filename=attachment.filename, spoiler=True))

        if len(images) > 0 or len(embeds) > 0:
            await message.channel.send(files=images, embeds=embeds)


def setup(bot):
    bot.add_cog(NSFWTesting(bot))
