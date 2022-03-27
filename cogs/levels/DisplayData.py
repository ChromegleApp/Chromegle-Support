import io
import math
from datetime import datetime
from typing import Tuple

import discord
from discord import Member
from discord.ext import commands
from discord_slash import SlashCommandOptionType, SlashContext
from dislash import OptionChoice, SlashInteraction
from dislash.slash_commands import Option

import config
from bot import ChromegleSupport
from cogs.levels.Tracking import Leaderboard
from modules import CardGenerator

LEADERBOARD_TYPES: dict = {
    config.LevelSystem.LEADERBOARD_WEEKLY: "Weekly Leaderboard",
    config.LevelSystem.LEADERBOARD_MONTHLY: "Monthly Leaderboard",
    config.LevelSystem.LEADERBOARD_FOREVER: "All-Time Leaderboard"
}


class DisplayData(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @ChromegleSupport.inter_client.slash_command(
        name="leaderboard",
        description="Get the xp leaderboard for the discord",
        options=[
            Option("board", "Choose the leaderboard type", SlashCommandOptionType.STRING, False, choices=[
                OptionChoice(name=LEADERBOARD_TYPES[config.LevelSystem.LEADERBOARD_WEEKLY], value=config.LevelSystem.LEADERBOARD_WEEKLY),
                OptionChoice(name=LEADERBOARD_TYPES[config.LevelSystem.LEADERBOARD_MONTHLY], value=config.LevelSystem.LEADERBOARD_MONTHLY),
                OptionChoice(name=LEADERBOARD_TYPES[config.LevelSystem.LEADERBOARD_FOREVER], value=config.LevelSystem.LEADERBOARD_FOREVER)
            ]),
            Option("page", "Choose the leaderboard page", SlashCommandOptionType.INTEGER, False)
        ],
        guild_ids=[config.HOME_GUILD_ID]
    )
    async def leaderboard(self, context: SlashContext, board: str = None, page: int = 1):
        board = board if board is not None else config.LevelSystem.LEADERBOARD_FOREVER

        leaderboard: Leaderboard = Leaderboard(config.LevelSystem.DB_PATH, board)
        leaderboard.connect()
        top_users: Tuple[int] = leaderboard.retrieve_top_users(limit=config.LevelSystem.Leaderboard.LIMIT_USERS)
        leaderboard.disconnect()

        # Collect info from raw data
        raw_length = len(top_users)  # Number of results
        raw_pages = math.ceil(raw_length / config.LevelSystem.Leaderboard.RESULTS_PER_PAGE)

        if page < 0:
            page = 1
        elif page > raw_pages:
            page = raw_pages

        # Get the data at the page index
        data_index = (page - 1) * config.LevelSystem.Leaderboard.RESULTS_PER_PAGE
        selected_data = top_users[data_index:data_index + config.LevelSystem.Leaderboard.RESULTS_PER_PAGE]

        leaderboard_users = ""
        leaderboard_levels_xp = ""

        levels_length, xp_length, messages_length = [], [], []

        for item in selected_data:
            levels_length.append(len('{:,}'.format(Leaderboard.calculate_level(item[1]))))
            xp_length.append(len('{:,}'.format(item[1])))
            messages_length.append(int(len(str('{:,}'.format(item[2])))))

        for idx, item in enumerate(selected_data):
            val = idx + data_index + 1
            val = "🥇" if val == 1 else val
            val = "🥈" if val == 2 else val
            val = "🥉" if val == 3 else val
            val = f"`{val}.`" if type(val) == int else val

            __uuid = item[0]
            __level = '{:,}'.format(Leaderboard.calculate_level(item[1]))
            __xp = '{:,}'.format(item[1])
            __messages = '{:,}'.format(item[2])

            leaderboard_users += f"{val} {'<@' + str(__uuid) + '>' if context.guild.get_member(user_id=__uuid) is not None else '**Not Available (Left Guild)**'}\n"
            leaderboard_levels_xp += f"` {__level}{' ' * (max(levels_length) - len(__level))} 🏅 | {__xp} {' ' * (max(xp_length) - len(__xp))}📊 | {__messages}{' ' * (max(messages_length) - len(__messages))} 💬 `\n"

        embed = discord.Embed(
            title=f":trophy:  {LEADERBOARD_TYPES[board]} - Page {page}/{raw_pages}",
            color=config.EMBED_COLOUR_STRD,
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="Member",
            value=leaderboard_users
        )
        embed.add_field(
            name="Levels | Experience | Messages",
            value=leaderboard_levels_xp
        )
        embed.set_footer(
            icon_url=self.bot.user.avatar_url,
            text=f'{context.guild.name}'
        )

        await context.reply(embed=embed)

    @ChromegleSupport.inter_client.slash_command(
        name="rank",
        description="Get a member's rank statistics",
        options=[
            Option("member", "The member to check stats for", SlashCommandOptionType.USER, False)
        ],
        guild_ids=[config.HOME_GUILD_ID]
    )
    async def rank(self, context: SlashInteraction, member: Member = None):
        member = context.author if member is None else member

        if member.bot:
            return await context.reply(":x: Bots are not tracked within the ranking system!", ephemeral=True)

        leaderboard: Leaderboard = Leaderboard(config.LevelSystem.DB_PATH, config.LevelSystem.LEADERBOARD_FOREVER)
        leaderboard.connect()

        xp: int = leaderboard.retrieve_xp(member.id)
        level: int = leaderboard.calculate_level(xp)

        obtained_xp: int = xp - leaderboard.calculate_xp(level)
        needed_xp: int = leaderboard.calculate_xp(level + 1) - leaderboard.calculate_xp(level)
        position: int = leaderboard.retrieve_position(context.author.id)

        # Silliness
        if int(member.id) == 699802828356583435:
            level = 69420
            position = 1

        image = await CardGenerator.create_card(member, obtained_xp, needed_xp, position if xp > 0 else None, level)

        with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await context.reply(f"Fetching the rank card for **{str(member).replace('`', '')}**...", ephemeral=True)

            embed = discord.Embed(
                colour=config.EMBED_COLOUR_INVIS,
            )

            embed.set_image(url="attachment://rank_card.png")
            embed.set_author(name=f"Requested by {context.author}", icon_url=context.author.avatar_url)

            await context.reply(embed=embed, files=[discord.File(fp=image_binary, filename='rank_card.png')])


def setup(bot):
    bot.add_cog(DisplayData(bot))
