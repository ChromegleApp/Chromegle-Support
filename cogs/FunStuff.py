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
                f"Chats Started: `{stats['within_ten_minutes']['chats_started']:,} times`\n"
                f"Chats Ended: `{stats['within_ten_minutes']['chats_ended']:,} times`\n"
                f"Omegle Opened: `{stats['within_ten_minutes']['times_opened']:,} times`\n"
            )

        )

        embed.add_field(
            name="All Time",
            value=(
                f"Chats Started: `{stats['all_time']['chats_started']:,} times`\n"
                f"Chats Ended: `{stats['all_time']['chats_ended']:,} times`\n"
                f"Omegle Opened: `{stats['all_time']['times_opened']:,} times`\n"
            )

        )

        await context.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(FunStuff(bot))
