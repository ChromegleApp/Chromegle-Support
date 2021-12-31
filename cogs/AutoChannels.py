import asyncio
import datetime
import logging
import traceback

from discord import TextChannel, VoiceChannel
from discord.ext import commands, tasks

import config
from modules.BotUtil import BotUtil


class AutoChannels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.extension_count = None
        self.omegle_count = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.short_channel_updates.start()
        self.topic_updates.start()

        await asyncio.sleep(15)
        self.long_channel_updates.start()

    @tasks.loop(minutes=69, reconnect=True)
    async def short_channel_updates(self):
        """
        Update channel counters every 30 minutes

        """

        print("Updating <Short> Voice Channel Topics @", datetime.datetime.utcnow())

        try:
            self.omegle_count = await BotUtil.get_omegle_count()
        except:
            logging.error(traceback.format_exc())
            print("Failed to retrieve new Omegle user count @", datetime.datetime.utcnow())

        if self.omegle_count is not None:
            omegle_users_channel: VoiceChannel = await self.bot.fetch_channel(config.CounterChannels.OMEGLE_COUNT_CHANNEL_ID)
            await omegle_users_channel.edit(
                name=config.CounterChannels.OMEGLE_COUNT_MESSAGE.replace(
                    config.CounterChannels.COUNT_STRING,
                    f"{BotUtil.reduce_granularity(self.omegle_count):,}+"
                )
            )

    @tasks.loop(hours=12, reconnect=True)
    async def long_channel_updates(self):
        """
        Update channel counters every 12h

        """

        print("Updating <Long> Voice Channel Topics @", datetime.datetime.utcnow())

        member_channel: VoiceChannel = await self.bot.fetch_channel(config.CounterChannels.MEMBER_COUNT_CHANNEL_ID)
        await member_channel.edit(
            name=config.CounterChannels.MEMBER_COUNT_MESSAGE.replace(config.CounterChannels.COUNT_STRING, f"{member_channel.guild.member_count:,}")
        )

        if self.extension_count is not None:
            user_channel: VoiceChannel = await self.bot.fetch_channel(config.CounterChannels.USER_COUNT_CHANNEL_ID)
            await user_channel.edit(
                name=config.CounterChannels.USER_COUNT_MESSAGE.replace(config.CounterChannels.COUNT_STRING, self.extension_count)
            )

    @tasks.loop(hours=12, reconnect=True)
    async def topic_updates(self):
        """
        Update channel topics every 12h

        """

        try:
            count = await BotUtil.get_extension_count()
            self.extension_count = count if count is not None else "N/A"
        except:
            logging.error(traceback.format_exc())
            print("Failed to retrieve new extension count @", datetime.datetime.utcnow())

        if self.extension_count is None:
            return

        print("Updating Text Channel Topics @", datetime.datetime.utcnow())
        for channel_id, channel_topic in config.TopicChannels.TOPIC_CHANNELS:
            channel: TextChannel = await self.bot.fetch_channel(channel_id)

            if channel.topic is None:
                continue

            topic = str(channel_topic).replace(config.TopicChannels.TOPIC_STRING, self.extension_count)

            if config.TopicChannels.TOPIC_STRING not in channel_topic:
                if str(channel.topic) == topic:
                    continue

            await channel.edit(topic=topic, reason="Topic Update")


def setup(bot):
    bot.add_cog(AutoChannels(bot))
