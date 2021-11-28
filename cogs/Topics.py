from discord import TextChannel
from discord.ext import commands, tasks
from modules.BotUtil import BotUtil
import config


class Topics(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.topic_updates.start()

    @tasks.loop(hours=6)
    async def topic_updates(self):
        """
        Update channel topics every 30m

        """

        user_count = await BotUtil.get_extension_count()

        if user_count is None:
            return

        for channel_id, channel_topic in config.TOPIC_CHANNELS:
            channel: TextChannel = await self.bot.fetch_channel(channel_id)

            if channel.topic is None:
                continue

            topic = str(channel_topic).replace(config.TOPIC_STRING, user_count)

            if config.TOPIC_STRING not in channel_topic:
                if str(channel.topic) == topic:
                    continue

            await channel.edit(topic=topic, reason="Topic Update")


def setup(bot):
    bot.add_cog(Topics(bot))
