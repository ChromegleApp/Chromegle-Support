import asyncio
import json
import logging
import os.path
import traceback
from typing import Optional, List, Tuple

import aiocron
from discord import Guild, Role, Member
from discord.ext import commands
from discord.ext.commands import Bot

import config
from cogs.levels.Tracking import Leaderboard


class Resetting(commands.Cog):
    """
    Crontab Calculator: https://crontab.guru/

    """

    __bot: Optional[Bot] = None
    __guild: Optional[Guild] = None
    __member_of_the_week: Optional[Role] = None

    def __init__(self, bot):
        Resetting.__bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Start tasks and load cached data on bot ready
        :return:

        """

        self.reset_weekly_tracking.start()
        self.reset_monthly_tracking.start()

    @classmethod
    async def __clear_leaderboard(cls, table_name):
        """
        Clear a leaderboard in the database given its table name
        :param table_name: The table name for the leaderboard
        :return: None

        """

        lb: Leaderboard = Leaderboard(config.LevelSystem.DB_PATH, table_name)
        lb.connect()
        lb.reset_leaderboard()
        lb.disconnect()

    @classmethod
    async def __clear_activity_roles(cls):
        """
        Clear activity roles
        :return: 
        """
        activity_roles: List[Role] = []

        for messages, role_id in config.LevelSystem.ActivityRoles.ACTIVITY_ROLES.items():
            activity_roles.append(Resetting.__bot.get_guild(config.HOME_GUILD_ID).get_role(role_id))

        # For each role
        for role in activity_roles:
            for member in role.members:
                await member.remove_roles(role)
                await asyncio.sleep(3)

    @classmethod
    async def __update_member_of_the_week(cls):
        """
        Update the member of the week
        :return: None

        """

        tracked_guild: Guild = Resetting.__bot.get_guild(config.HOME_GUILD_ID)
        member_of_the_week: Role = tracked_guild.get_role(config.LevelSystem.MEMBER_OF_THE_WEEK_ROLE)

        # Clear previous member(s)
        for member in member_of_the_week.members:
            await member.remove_roles(member_of_the_week)
            await asyncio.sleep(2)

        # Get top 10 from leaderboard
        leaderboard: Leaderboard = Leaderboard(config.LevelSystem.DB_PATH, config.LevelSystem.LEADERBOARD_WEEKLY)
        leaderboard.connect()
        top_10: List[Tuple] = leaderboard.retrieve_top_users()
        leaderboard.disconnect()

        # If no logged members yet, return
        if len(top_10) < 1:
            return

        # Get top member
        top_member: Tuple = top_10[0]
        member_id = top_member[0]

        try:
            member: Member = tracked_guild.get_member(member_id)
        except:
            logging.error("Unable to get top leaderboard member for Member of the Week, they probably left the Guild")
            return

        # Add the role to them
        await member.add_roles(member_of_the_week)

        # Create if not exists
        if not os.path.exists(config.LevelSystem.JSON_PATH):
            open(config.LevelSystem.JSON_PATH, "w", encoding="utf-8").write("{}")

        # Get JSON data
        with open(config.LevelSystem.JSON_PATH, 'r', encoding='utf-8') as file:
            data: dict = json.loads(file.read())
            data["motw"] = member_id

        # Update JSON data
        with open(config.LevelSystem.JSON_PATH, 'w+', encoding='utf-8') as file:
            file.write(json.dumps(data, indent=4))

    @staticmethod
    @aiocron.crontab("0 0 * * MON", start=False)  # 0 0 * * MON         <= Weekly (Every Monday)
    async def reset_weekly_tracking():
        """
        Reset the weekly leaderboard every week
        
        """
        try:
            await Resetting.__update_member_of_the_week()
            await Resetting.__clear_leaderboard(config.LevelSystem.LEADERBOARD_WEEKLY)
            await Resetting.__clear_activity_roles()
        except:
            logging.error(traceback.format_exc())

    @staticmethod
    @aiocron.crontab("0 0 1 * *", start=False)  # 0 0 1 * *         <= Monthly (On the 1st of Each Month)
    async def reset_monthly_tracking():
        """
        Reset the monthly leaderboard every month

        """
        try:
            await Resetting.__clear_leaderboard(config.LevelSystem.LEADERBOARD_MONTHLY)
        except:
            logging.error(traceback.format_exc())


def setup(bot):
    bot.add_cog(Resetting(bot))
