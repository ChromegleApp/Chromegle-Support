import platform, os
import discord
from discord.ext import tasks
from discord.ext.commands import Bot
import config


bot = Bot(command_prefix=config.BOT_PREFIX, case_insensitive=True, intents=discord.Intents().all())
bot.remove_command("help")


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


    bot.run(open("resources/bot_token.txt").read())
