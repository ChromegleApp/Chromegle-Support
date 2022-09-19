import aiohttp
import discord
from discord.ext import commands

import config


class FunStuff(commands.Cog):

    def __int__(self, bot):
        self.bot = bot

    @commands.command(name="rock")
    async def rock(self, context):
        await context.reply("https://tenor.com/view/rock-one-eyebrow-raised-rock-staring-the-rock-gif-22113367", mention_author=False)

    @classmethod
    async def _get_stats(cls):
        async with aiohttp.ClientSession() as session:
            async with session.get(url="https://chromegle.isaackogan.com/chromegle/stats") as request:
                return await request.json()

    @commands.command(name="stats")
    async def stats(self, context):
        stats: dict = (await self._get_stats())["payload"]
        embed: discord.Embed = discord.Embed(
            title="Chromegle Statistics",
            colour=config.EMBED_COLOUR_STRD,
            description=f"There are currently **{stats['online_users']}** Chromeglers Online"
        )

        embed.add_field(
            name="Within 10 Minutes",
            value=(
                f"Chats Started: `{stats['ten_minutes']['chats_started']:,} times`\n"
                f"Chats Ended: `{stats['ten_minutes']['chats_ended']:,} times`\n"
                f"Omegle Opened: `{stats['ten_minutes']['times_opened']:,} times`\n"
            ),
            inline=False

        )

        embed.add_field(
            name="Since Midnight",
            value=(
                f"Chats Started: `{stats['today']['chats_started']:,} times`\n"
                f"Chats Ended: `{stats['today']['chats_ended']:,} times`\n"
                f"Omegle Opened: `{stats['today']['times_opened']:,} times`\n"
            ),
            inline=False

        )

        embed.add_field(
            name="Within 7 Days",
            value=(
                f"Chats Started: `{stats['week']['chats_started']:,} times`\n"
                f"Chats Ended: `{stats['week']['chats_ended']:,} times`\n"
                f"Omegle Opened: `{stats['week']['times_opened']:,} times`\n"
            ),
            inline=False

        )

        embed.add_field(
            name="Within All Time",
            value=(
                f"Chats Started: `{stats['forever']['chats_started']:,} times`\n"
                f"Chats Ended: `{stats['forever']['chats_ended']:,} times`\n"
                f"Omegle Opened: `{stats['forever']['times_opened']:,} times`\n"
            ),
            inline=False

        )

        await context.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(FunStuff(bot))
