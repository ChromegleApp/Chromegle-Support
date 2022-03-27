import math
import random
import sqlite3
from typing import Optional, Tuple, List

import discord
from discord import Message, Member, Guild
from discord.ext import commands

import config


class Leaderboard:

    def __init__(self, db_path: str, table_name: str):
        self.db_path: str = db_path
        self.table_name: str = table_name
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def connect(self):
        """
        Connect to database
        :return: None
        
        """

        self.conn: sqlite3.Connection = sqlite3.connect(config.LevelSystem.DB_PATH)
        self.cursor: sqlite3.Cursor = self.conn.cursor()

    def disconnect(self):
        """
        Disconnect from database connection
        :return: None
        
        """
        self.cursor.close()
        self.conn.close()

        self.conn = None
        self.cursor = None

    def increment_xp(self, discord_id: str, add_experience: int):
        """
        Increment a user's experience

        :param add_experience: Amount of experience to add
        :param discord_id: Their discord ID
        :return: None

        """
        self.cursor.execute(
            f"INSERT INTO {self.table_name} (discord_id, experience, messages) VALUES ({int(discord_id)}, {int(add_experience)}, 0) "
            f"ON CONFLICT (discord_id) DO UPDATE SET experience = experience + {int(add_experience)}"
        )

        self.cursor.execute(
            f"UPDATE {self.table_name} SET messages = messages + 1 WHERE discord_id={discord_id}"
        )

        self.conn.commit()

    def retrieve_xp(self, discord_id: str):
        """
        Retrieve a user's experience

        :param discord_id: Their discord ID
        :return: Their experience

        """

        discord_id: int = int(discord_id)
        self.cursor.execute(f"SELECT experience FROM {self.table_name} WHERE discord_id={discord_id}")
        result: Optional[Tuple] = self.cursor.fetchone()
        return result[0] if result is not None else 0

    def retrieve_messages(self, discord_id: str):
        """
        Retrieve a user's message count

        :param discord_id: Their discord ID
        :return: Their message count

        """

        discord_id: int = int(discord_id)
        self.cursor.execute(f"SELECT messages FROM {self.table_name} WHERE discord_id={discord_id}")
        result: Optional[Tuple] = self.cursor.fetchone()
        return result[0] if result is not None else 0

    def retrieve_top_users(self, limit: int = 10):
        """
        Retrieve the top 10 of the leaderboard
        :return: The top 10 metric

        """

        self.cursor.execute(f"SELECT discord_id, experience, messages FROM {self.table_name} ORDER BY experience DESC LIMIT {limit}")
        return self.cursor.fetchall()

    def retrieve_position(self, discord_id: int) -> int:
        self.cursor.execute(
            f"""
                SELECT
                    count(*)
                FROM
                    leaderboard_forever
                WHERE
                    experience > (SELECT experience FROM leaderboard_forever WHERE discord_id = {int(discord_id)})
            """
        )
        result: Optional[Tuple] = self.cursor.fetchone()
        return result[0] + 1 if result is not None else -1

    def reset_leaderboard(self):
        """
        Reset the database by clearing all stored values
        :return: None

        """

        self.cursor.execute(f"DELETE FROM {self.table_name};")
        self.conn.commit()

    @classmethod
    def calculate_level(cls, xp: int):
        """
        Formula: g(x) = sqrt(10)/10 * sqrt(x)
        Calculate a user's level from their XP

        Level 100 = 100,000 XP
        At ~5xp/message, that's 20,000 messages

        :param xp: Experience
        :return: Level

        """

        return abs(
            math.floor((math.sqrt(10) / 10) * math.sqrt(xp))
        )

    @classmethod
    def calculate_xp(cls, level: int):
        """
        g(x) = 10x^2
        Inverse of the level calculation

        :param level: Their level
        :return: Their experience
        """

        return abs(
            10 * (math.floor(level) ** 2)
        )


class Tracking(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.initialize()

        self.guild: Optional[Guild] = None
        self.level_role_list: Optional[list] = None
        self.activity_role_cache: dict = dict()
        self.level_role_cache: dict = dict()

    @classmethod
    def initialize(cls):
        """
        Create the database tables
        :return: None

        """

        conn: sqlite3.Connection = sqlite3.connect(config.LevelSystem.DB_PATH)
        cursor: sqlite3.Cursor = conn.cursor()

        # Create table for each leaderboard
        for table_name in [config.LevelSystem.LEADERBOARD_WEEKLY, config.LevelSystem.LEADERBOARD_MONTHLY, config.LevelSystem.LEADERBOARD_FOREVER]:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (discord_id INTEGER PRIMARY KEY, experience INTEGER, messages INTEGER)")

        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Load role data for rank-ups on bot ready
        :return: None

        """

        self.guild = self.bot.get_guild(config.HOME_GUILD_ID)
        self.level_role_list = sorted(list(config.LevelSystem.LEVEL_ROLES.keys()))

        # Get level roles
        for level, role_id in config.LevelSystem.LEVEL_ROLES.items():
            self.level_role_cache[level] = self.guild.get_role(role_id)

        # Get activity roles
        for messages, role_id in config.LevelSystem.ActivityRoles.ACTIVITY_ROLES.items():
            self.activity_role_cache[messages] = self.guild.get_role(role_id)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """
        Track user experience on message event
        :param message: Message sent

        """

        # Bot not ready
        if not self.activity_role_cache:
            return

        # Not in guild
        if not message.guild or message.guild.id != config.HOME_GUILD_ID:
            return

        # Bot or not in chat channel
        if message.author.bot or (int(message.channel.id) in config.LevelSystem.BLACKLISTED_CHANNELS):
            return

        # Is a command
        if str(message.content).startswith(config.BOT_PREFIX):
            return

        # Update XP for all-time leaderboard
        old_level, new_level, add_experience = await self.forever_leaderboard(message)

        await self.timed_leaderboard(message, config.LevelSystem.LEADERBOARD_MONTHLY, add_experience)
        old_weekly_messages, new_weekly_messages = await self.timed_leaderboard(message, config.LevelSystem.LEADERBOARD_WEEKLY, add_experience)

        # Levels => Ranking Up
        if new_level > old_level:
            await self.__rank_up_member(message, message.author, new_level)

        # Activity => Ranking Up
        await self.__activity_rankup_member(message, old_weekly_messages, new_weekly_messages)

    async def __activity_rankup_member(self, message: Message, old_messages: int, new_messages: int):
        """
        Rank up members based on activity

        :param message: Message they sent
        :param old_messages: Number of messages previously
        :param new_messages: Number of messages now
        :return: None

        """

        add_roles: List[discord.Role] = []
        for messages, role in self.activity_role_cache.items():
            # If it was < X before and >= X now, add role
            if old_messages < messages <= new_messages:
                add_roles.append(role)
                await self.__activity_rankup_reply(message, messages, role)

        if len(add_roles) > 0:
            await message.author.add_roles(*add_roles)

    @classmethod
    async def __activity_rankup_reply(cls, message: Message, messages: int, role: discord.Role):
        """
        Send a rank-up message when someone meets the activity threshold
        :param message: Message to reply to
        :return: None

        """

        try:
            await message.reply(
                embed=discord.Embed(
                    title=f"Great job {message.author.name}, you're on fire! :fire:",
                    description=(
                        f"Well done! Congratulations on `{messages:,} Messages` this week!\n\n"
                        f"You just received the {role.mention} role for your hard work!"
                    ),
                    color=config.EMBED_COLOUR_STRD
                ).set_footer(
                    text="Keep talking to level up for more rewards!"
                ).set_thumbnail(
                    url=config.BrandInfo.ANIMATED_LOGO
                )
            )
        except:
            pass

    @classmethod
    async def timed_leaderboard(cls, message: Message, table_name: str, add_experience: int):
        """
        Increment values for a timed, resettable leaderboard

        :param message: Message object
        :param table_name: Table name for timed leaderboard
        :param add_experience: Amount of experience to add based on forever leaderboard
        :return: None

        """

        lb: Leaderboard = Leaderboard(config.LevelSystem.DB_PATH, table_name)
        lb.connect()

        old_messages: int = lb.retrieve_messages(message.author.id)
        lb.increment_xp(message.author.id, add_experience)
        new_messages: int = lb.retrieve_messages(message.author.id)

        lb.disconnect()
        return old_messages, new_messages

    @classmethod
    async def forever_leaderboard(cls, message: Message) -> Tuple[int, int, int]:
        """
        Increment values on the forever leaderboard & return level before & after & how much XP was added

        :param message: Message object
        :return: Tuple[XP Before, XP After]

        """
        lb: Leaderboard = Leaderboard(config.LevelSystem.DB_PATH, "leaderboard_forever")
        lb.connect()

        # Get old XP
        old_xp: int = lb.retrieve_xp(message.author.id)
        old_level: int = lb.calculate_level(old_xp)

        add_experience: int = abs(random.randint(config.LevelSystem.MIN_ADD_XP, config.LevelSystem.MAX_ADD_XP))

        # Less than level 10 should give 1/3 the normal XP
        if old_level <= 10:
            add_experience = math.floor(add_experience / 2)

        # Increment XP
        lb.increment_xp(message.author.id, add_experience)

        # Get new XP
        new_xp: int = lb.retrieve_xp(message.author.id)
        new_level: int = lb.calculate_level(new_xp)

        lb.disconnect()

        return old_level, new_level, add_experience

    async def __rank_up_member(self, message: Message, member: Member, new_level: int):
        """
        Run certain actions when a person ranks up in a channel

        :param message: Message to reply to
        :param member: Member to run the actions on
        :param new_level: Their new level

        :return: None

        """

        # Send the level-up message
        await message.reply(
            embed=discord.Embed(
                title=f"Keep it up {message.author.name}, you're on fire! :fire:",
                description=(
                    f"Well done! Congratulations on `Level {new_level:,}`!\n\n"
                    f"Use `/rank` in <#{config.LevelSystem.BOT_COMMANDS_CHANNEL}> to see your rank card."
                ),
                color=config.EMBED_COLOUR_STRD
            ).set_footer(
                text="Keep talking to level up for more rewards!"
            ).set_thumbnail(
                url=config.BrandInfo.ANIMATED_LOGO
            )
        )

        # Rank-up Roles
        try:
            await self.__rank_up_role(member, new_level, self.level_role_list.index(new_level))
        except:
            pass

    async def __rank_up_role(self, member: Member, new_level: int, role_index: int):
        """
        Give rank-up roles

        :param member: Member to give roles to
        :param new_level: New level
        :param role_index: Index of last role
        :return: None

        """

        new_role = self.level_role_cache.get(new_level)
        old_role = self.level_role_cache.get(self.level_role_list[role_index - 1]) if role_index > 0 else None

        if new_role is not None:
            await member.add_roles(new_role)

        if old_role is not None:
            await member.remove_roles(old_role)


def setup(bot):
    bot.add_cog(Tracking(bot))
