from __future__ import annotations

import os
import platform
from typing import Optional

import discord
from discord.ext.commands import Bot
from dislash import InteractionClient

import config
from modules.FileUtils import file_type_search


class ChromegleSupport(Bot):
    inter_client: Optional[InteractionClient] = None

    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        ChromegleSupport.inter_client = InteractionClient(self, sync_commands=True)
        self.remove_command("help")

    async def on_ready(self) -> None:
        """
        Send some start-up messages on Bot Ready State
        :return: None

        """
        print("-------------------")
        print(f"Logged in as {self.user.name}")
        print(f"Discord.py API version: {discord.__version__}")
        print(f"Python version: {platform.python_version()}")
        print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        print("Go for launch!")
        print("-------------------")

    async def on_message(self, message):
        # Ignores Bot Messages
        if message.author == bot.user or message.author.bot:
            return

        # No DMs Sadly
        if not message.guild:
            return

        await bot.process_commands(message)

    def load_extensions(self) -> ChromegleSupport:
        """
        Load bot extensions from recursive file search
        :return: None

        """

        cogs: list = [cog.replace("./", "").replace("/", ".").replace(".py", "") for cog in file_type_search('./cogs', '.py')]

        for cog in cogs:
            try:
                self.load_extension(cog)
                print(f"[COG] Loaded bot extension", f"/{cog.replace('.', '/')}.py")
            except Exception as ex:
                print(f"Failed to load extension", cog, f"{type(ex).__name__}: {ex}")

        return self


bot = (
    ChromegleSupport(
        command_prefix=config.BOT_PREFIX,
        help_command=None,
        intents=discord.Intents.all(),
        case_insensitive=True,
        sync_commands=False
    ).load_extensions()
)

if __name__ == '__main__':
    """
    Invite via 1021515865499385958
    """
    bot.run(open("resources/bot_token.txt").read())
