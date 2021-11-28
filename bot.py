import asyncio
import platform, os
import discord
from aiohttp.web_app import Application
from aiohttp.web_runner import AppRunner, TCPSite
from discord.ext import tasks
from discord.ext.commands import Bot
import config
from api import routes
import nest_asyncio

intents = discord.Intents().all()

bot = Bot(command_prefix=config.BOT_PREFIX, case_insensitive=True, intents=intents)
bot.remove_command("help")

import config


class BotAPI:

    def __init__(self, hostname, port, bot, routes):

        # Configuration
        self.hostname = hostname
        self.port = port

        # App
        self.app = Application()
        self.app['bot'] = {'cache': bot}
        self.app.add_routes(routes)

        # Runner
        self.routes = routes
        self.runner = AppRunner(self.app)

        # Site
        self.site = None

    async def run(self):
        await self.runner.setup()
        self.site = TCPSite(self.runner, self.hostname, self.port)
        await self.site.start()
        print(f'Bot API is enabled at \"{self.hostname}:{self.port}\"')


@tasks.loop(seconds=5)
async def update_api_bot_data():
    bot_api.app['bot']['cache'] = bot

@bot.event
async def on_ready():
    print("-------------------")
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("Go for launch!")
    print("-------------------")



@bot.event
async def on_message(message):

    # Ignores Bot Messages
    if message.author == bot.user or message.author.bot:
        return

    # No DMs Sadly
    if isinstance(message.channel, discord.channel.DMChannel):
        return

    await bot.process_commands(message)


@bot.event
async def on_command_error(context, error):
    if context.command is not None:
        if context.command.has_error_handler():
            return

    # No command? Ignore.
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        return

    raise error


if __name__ == "__main__":
    for (dirpath, dirnames, filenames) in os.walk(config.COG_PATH):
        for file in filenames:
            if file.endswith(".py"):
                cog = f"{config.COG_PATH[2:]}.{file.replace('.py', '')}"
                try:
                    bot.load_extension(cog)
                    print(f"[COG] Loaded bot extension {(cog[cog.rfind('.') + 1:]).lower()}.py")
                except Exception as ex:
                    exception = f"{type(ex).__name__}: {ex}"
                    print(f"Failed to load extension {cog}\n{exception}")

    # Run the Bot
    nest_asyncio.apply()

    loop = asyncio.get_event_loop()
    bot_api = BotAPI('0.0.0.0', 25581, bot, routes)
    asyncio.run_coroutine_threadsafe(bot_api.run(), loop)

    # Enable the update task
    update_api_bot_data.start()


    bot.run(open("resources/bot_token.txt").read())
