import json
import time

import discord
from discord import Message
from discord.ext import commands, tasks

import config


class Support(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.last_message_time = 0

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel = await self.bot.fetch_channel(config.AUTO_MESSAGE_CHANNEL)
        self.auto_message.start()

    @commands.Cog.listener()
    async def on_message(self, message):

        # Must be a channel
        if not message.channel:
            return

        # Must be valid
        if not self.channel:
            return

        # Must be correct channel
        if not int(message.channel.id) == int(self.channel.id):
            return

        # No Bots
        if message.author.bot:
            return

        # Update the most recent timing
        self.last_message_time = int(time.time())

    @tasks.loop(seconds=60)
    async def auto_message(self):

        # Too soon
        if (int(time.time()) - self.last_message_time) < 120:
            return

        # Load the json data
        with open(config.DATA_PATH) as file:
            data: dict = json.loads(file.read())

        # Get messages to compare
        message: Message = await self.channel.history().get()
        old_message_id: int = data.get('SupportMessageID', 0)

        if message is not None:
            # Same? Buh-bye
            if int(message.id) == int(old_message_id):
                return

            # Get the old message object
            try: m = await self.channel.fetch_message(old_message_id)
            except: m = None

            # Remove the old message
            if m is not None:
                await m.delete()

        # Paste the new message
        eb = discord.Embed(
            title="So... you need help? We've got you covered!",
            description=(
                "If you need information on downloading Chromegle, check <#922237065222029352> before "
                f"asking here. Otherwise, if you think your question is a common one, it might have been "
                f"answered in <#922237064215412816> too. If all else fails, feel free to ask a question "
                f"and we'll try to figure it out. Regards from the creator, `{await self.channel.guild.fetch_member(config.BOT_OWNER_ID)}`."
            ),
            colour=config.EMBED_COLOUR_STRD
        )

        new_message: Message = await message.channel.send(embed=eb)

        # Load the json data
        with open(config.DATA_PATH) as file:
            data: dict = json.loads(file.read())
            data['SupportMessageID'] = new_message.id

        with open(config.DATA_PATH, 'w') as file:
            file.write(json.dumps(data, indent=4))


def setup(bot):
    bot.add_cog(Support(bot))
