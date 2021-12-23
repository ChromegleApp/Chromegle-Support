import asyncio
import logging
import traceback
import datetime

from discord import TextChannel, VoiceChannel
from discord.ext import commands, tasks
from modules.BotUtil import BotUtil
import config


class AutoChannels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.count = "N/A"

    @commands.Cog.listener()
    async def on_ready(self):
        self.topic_updates.start()
        await asyncio.sleep(15)
        self.channel_updates.start()

    @tasks.loop(hours=12, reconnect=True)
    async def channel_updates(self):
        """
        Update channel counters every 12h

        """

        if self.count is None:
            return

        print("Updating Voice Channel Topics @", datetime.datetime.utcnow())

        member_channel: VoiceChannel = await self.bot.fetch_channel(config.CounterChannels.MEMBER_COUNT_CHANNEL_ID)
        await member_channel.edit(
            name=config.CounterChannels.MEMBER_COUNT_MESSAGE.replace(config.CounterChannels.COUNT_STRING, f"{member_channel.guild.member_count:,}")
        )

        user_channel: VoiceChannel = await self.bot.fetch_channel(config.CounterChannels.USER_COUNT_CHANNEL_ID)
        await user_channel.edit(
            name=config.CounterChannels.USER_COUNT_MESSAGE.replace(config.CounterChannels.COUNT_STRING, "N/A" if self.count is None else self.count)
        )

    @tasks.loop(hours=12, reconnect=True)
    async def topic_updates(self):
        """
        Update channel topics every 12h

        """

        try:
            self.count = await BotUtil.get_extension_count()
        except:
            logging.error(traceback.format_exc())
            print("Failed to retrieve new extension count @", datetime.datetime.utcnow())

        if self.count is None:
            return

        print("Updating Text Channel Topics @", datetime.datetime.utcnow())
        for channel_id, channel_topic in config.TopicChannels.TOPIC_CHANNELS:
            channel: TextChannel = await self.bot.fetch_channel(channel_id)

            if channel.topic is None:
                continue

            topic = str(channel_topic).replace(config.TopicChannels.TOPIC_STRING, self.count)

            if config.TopicChannels.TOPIC_STRING not in channel_topic:
                if str(channel.topic) == topic:
                    continue

            await channel.edit(topic=topic, reason="Topic Update")


def setup(bot):
    bot.add_cog(AutoChannels(bot))
