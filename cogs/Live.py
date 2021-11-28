from typing import Optional

import discord
from discord import Role, Guild
from discord.ext import commands, tasks

import config
from modules.BotUtil import BotUtil


class Live(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.streaming = []
        self.guild: Optional[Guild] = None
        self.creator: Optional[Role] = None
        self.live: Optional[Role] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(config.HOME_GUILD_ID)
        self.creator = self.guild.get_role(config.CONTENT_CREATOR_ROLE)
        self.live = self.guild.get_role(config.LIVE_CREATOR_ROLE)
        self.remove_un_sync.start()

    @staticmethod
    def is_streaming(member):
        return any(isinstance(activity, discord.activity.Streaming) for activity in member.activities)

    @tasks.loop(minutes=1)
    async def remove_un_sync(self):
        streaming = []

        # Remove un-sync
        for member in self.creator.members:
            if self.is_streaming(member):

                if self.live not in member.roles:
                    await member.add_roles(self.live)

                for activity in member.activities:

                    if isinstance(activity, discord.activity.Streaming):

                        if "omegle" in activity.name.lower() or "omegle" in str(activity.game).lower():
                            streaming.append(
                                (
                                    BotUtil.jsonify_member(member),
                                    {
                                        "url": activity.url,
                                        "name": activity.name,
                                        "platform": activity.platform,
                                        "game": activity.game
                                    }
                                )
                            )

            if not self.is_streaming(member) and self.live in member.roles:
                await member.remove_roles(self.live)

        # Update API
        self.bot.streaming = [{"member": stream[0], "stream": stream[1]} for stream in streaming]


    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        # If the creator hasn't loaded yet
        if self.creator is None or self.creator not in after.roles:
            return

        if not self.is_streaming(before) and self.is_streaming(after):
            if self.live not in after.roles:
                await after.add_roles(self.live)

        if self.is_streaming(before) and not self.is_streaming(after):
            if self.live in after.roles:
                await after.remove_roles(self.live)



def setup(bot):
    bot.add_cog(Live(bot))
