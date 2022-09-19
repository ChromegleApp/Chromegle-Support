import asyncio
import datetime
import json
import os
import time
from typing import Optional, List, Tuple

import discord
from discord import TextChannel
from discord.ext import commands, tasks

import config
from cogs.levels.Tracking import Leaderboard


class ChannelBoards(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.leaderboard_channel: Optional[TextChannel] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.leaderboard_channel: TextChannel = self.bot.get_channel(config.LevelSystem.ChannelBoards.BOARD_CHANNEL)
        await asyncio.sleep(30)
        await self.update_channel_boards.start()

    @classmethod
    def __get_rankings(cls, top_users) -> str:
        ranks: List[str] = []
        for idx, user_id in enumerate(top_users[:10]):
            ranks.append(
                f"<:{config.LevelSystem.ChannelBoards.EMOJIS.get(idx + 1)}> <@{user_id[0]}> `-` **{user_id[1]:,}** <:{config.LevelSystem.ChannelBoards.EMOJIS.get('xp')}>"
            )

        return '\n'.join(ranks)

    async def __generate_weekly_board(self) -> discord.Embed:
        leaderboard: Leaderboard = Leaderboard(config.LevelSystem.DB_PATH, config.LevelSystem.LEADERBOARD_WEEKLY)
        leaderboard.connect()
        top_10: List[Tuple] = leaderboard.retrieve_top_users()
        leaderboard.disconnect()

        # Create if not exists
        if not os.path.exists(config.LevelSystem.JSON_PATH):
            open(config.LevelSystem.JSON_PATH, "w", encoding="utf-8").write("{}")

        # Get JSON data
        with open(config.LevelSystem.JSON_PATH, 'r', encoding='utf-8') as file:
            data: dict = json.loads(file.read())
            motw: int = data.get("motw", self.bot.user.id)

        embed = discord.Embed(
            title="Chromegle XP Leaderboard [Weekly]",
            colour=config.EMBED_COLOUR_INVIS,
            description="_ _",
            timestamp=datetime.datetime.utcnow()
        )

        embed.set_thumbnail(
            url=str(self.bot.user.avatar_url)
        )

        embed.add_field(
            name=f"<{config.LevelSystem.ChannelBoards.EMOJIS.get('lb_crown', 'lb_crown')}> __**Member of the Week**__",
            value=(
                f"_ _\n<@{motw}> is the current <@&{config.LevelSystem.MEMBER_OF_THE_WEEK_ROLE}>\n\n_ _"
            ),
            inline=False
        )

        today = datetime.date.today()
        coming_monday: datetime.date = today + datetime.timedelta(days=-today.weekday(), weeks=1)
        monday_timestamp: int = round(time.mktime(coming_monday.timetuple()))

        embed.add_field(
            name=f":timer: __**Leaderboard Reset**__",
            value=f"_ _\nAutomatic reset <t:{monday_timestamp}:R>.\n\n_ _",
            inline=False
        )

        embed.add_field(
            name=":medal: __**Leaderboard Rankings**__",
            value=f"_ _\n{self.__get_rankings(top_10)}\n\n_ _",
            inline=False
        )

        embed.set_footer(
            text=f"Updates Every {config.LevelSystem.ChannelBoards.UPDATE_MINUTES} Minutes"
        )

        return embed

    async def __generate_monthly_board(self) -> discord.Embed:
        leaderboard: Leaderboard = Leaderboard(config.LevelSystem.DB_PATH, config.LevelSystem.LEADERBOARD_MONTHLY)
        leaderboard.connect()
        top_10: List[Tuple] = leaderboard.retrieve_top_users()
        leaderboard.disconnect()

        embed = discord.Embed(
            title="Chromegle XP Leaderboard [Monthly]",
            colour=config.EMBED_COLOUR_INVIS,
            description="_ _",
            timestamp=datetime.datetime.utcnow()
        )

        embed.set_thumbnail(
            url=str(self.bot.user.avatar_url)
        )

        today = datetime.date.today()
        first_of_month = today.replace(month=today.month + 1, day=1)
        monday_timestamp: int = round(time.mktime(first_of_month.timetuple()))

        embed.add_field(
            name=f":timer: __**Leaderboard Reset**__",
            value=f"_ _\nAutomatic reset <t:{monday_timestamp}:R>.\n\n_ _",
            inline=False
        )

        embed.add_field(
            name=":medal: __**Leaderboard Rankings**__",
            value=f"_ _\n{self.__get_rankings(top_10)}\n\n_ _",
            inline=False
        )

        embed.set_footer(
            text=f"Updates Every {config.LevelSystem.ChannelBoards.UPDATE_MINUTES} Minutes"
        )

        return embed

    async def __generate_forever_board(self) -> discord.Embed:
        leaderboard: Leaderboard = Leaderboard(config.LevelSystem.DB_PATH, config.LevelSystem.LEADERBOARD_FOREVER)
        leaderboard.connect()
        top_10: List[Tuple] = leaderboard.retrieve_top_users()
        leaderboard.disconnect()

        embed = discord.Embed(
            title="Chromegle XP Leaderboard [All Time]",
            colour=config.EMBED_COLOUR_INVIS,
            description="_ _",
            timestamp=datetime.datetime.utcnow()
        )

        embed.set_thumbnail(
            url=str(self.bot.user.avatar_url)
        )

        embed.add_field(
            name=":medal: __**Leaderboard Rankings**__",
            value=f"_ _\n{self.__get_rankings(top_10)}\n\n_ _",
            inline=False
        )

        embed.set_footer(
            text=f"Updates Every {config.LevelSystem.ChannelBoards.UPDATE_MINUTES} Minutes"
        )

        return embed

    @tasks.loop(minutes=5, reconnect=True)
    async def update_channel_boards(self):
        weekly_embed: discord.Embed = await self.__generate_weekly_board()
        monthly_embed: discord.Embed = await self.__generate_monthly_board()
        forever_embed: discord.Embed = await self.__generate_forever_board()

        # Create if not exists
        if not os.path.exists(config.LevelSystem.JSON_PATH):
            open(config.LevelSystem.JSON_PATH, "w", encoding="utf-8").write("{}")

        # Get JSON data
        with open(config.LevelSystem.JSON_PATH, 'r', encoding='utf-8') as file:
            data: dict = json.loads(file.read())

            weekly_message_id = data.get("weekly_message_id")
            monthly_message_id = data.get("monthly_message_id")
            forever_message_id = data.get("forever_message_id")
        # Forever
        try:
            forever_message = await self.leaderboard_channel.fetch_message(forever_message_id)
            await forever_message.edit(embed=forever_embed)
        except:
            forever_message = await self.leaderboard_channel.send(embed=forever_embed)

        # Monthly
        try:
            monthly_message = await self.leaderboard_channel.fetch_message(monthly_message_id)
            await monthly_message.edit(embed=monthly_embed)
        except:
            monthly_message = await self.leaderboard_channel.send(embed=monthly_embed)

        # Weekly
        try:
            weekly_message = await self.leaderboard_channel.fetch_message(weekly_message_id)
            await weekly_message.edit(embed=weekly_embed)
        except:
            weekly_message = await self.leaderboard_channel.send(embed=weekly_embed)

        # Update JSON data
        with open(config.LevelSystem.JSON_PATH, 'w+', encoding='utf-8') as file:
            data["weekly_message_id"] = int(weekly_message.id)
            data["monthly_message_id"] = int(monthly_message.id)
            data["forever_message_id"] = int(forever_message.id)

            file.write(json.dumps(data, indent=4))


def setup(bot):
    bot.add_cog(ChannelBoards(bot))
