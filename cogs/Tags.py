import discord
from discord.ext import commands

import config

from modules.TagItem import TagItem
from modules.BotUtil import BotUtil


class Tags(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    keywords = [
        'create', 'embed', 'delete', 'remove', 'list'
    ]

    @commands.command()
    async def tag(self, context, *args):

        try: key: str = args[0]
        except: return await context.send(config.X_EMOJI + " Must specify a tag or subcommand")

        if key in Tags.keywords:

            # List tags
            if key == "list":
                await context.invoke(self.bot.get_command('list_tags'), *args)
                return

            # Got perms?
            if not int(context.author.id) in config.BOT_ADMINS:
                await context.send(config.X_EMOJI + " You must be a bot admin to interact with tags")
                return

            # Create a tag
            if key == 'create':
                await context.invoke(self.bot.get_command('create_tag'), *args)
                return

            # Toggle embed for a tag
            if key == 'embed':
                await context.invoke(self.bot.get_command('toggle_tag_embed'), *args)
                return

            # Remove tag
            if key in ['delete', 'remove']:
                await context.invoke(self.bot.get_command('remove_tag'), *args)
                return

        # Get a tag
        await context.invoke(self.bot.get_command('get_tag'), *args)

    @commands.command()
    async def toggle_tag_embed(self, context, *args):
        try:
            tag: TagItem = TagItem(args[1])
        except IndexError:
            return await context.send(config.X_EMOJI + f" You must specify a tag!")
        except:
            return await context.send(config.X_EMOJI + f" Tag `{args[1]}` does not exist!")

        TagItem.update_embed_bool(tag.name, not tag.embed)

        await context.send(config.CHECK_EMOJI + f" Set embed to `{not tag.embed}` for tag.")

    @commands.command()
    async def get_tag(self, context, *args):
        try: tag: TagItem = TagItem(args[0])
        except: return await context.send(config.X_EMOJI + f" Tag `{args[0]}` does not exist!")

        if tag.embed:
            owner = await context.guild.fetch_member(tag.owner)

            eb = discord.Embed(
                title=f"{tag.label.capitalize() if tag.label.islower() else tag.label}",
                description=tag.message,
                colour=config.EMBED_COLOUR_STRD
            )

            eb.set_footer(
                text=f"Created by {owner} • {BotUtil.time_from_unix(tag.create_time)}",
                icon_url=owner.avatar_url
            )

            return await context.send(embed=eb)

        await context.send(tag.message)

    # noinspection PyUnboundLocalVariable
    @commands.command()
    async def create_tag(self, context, *args):

        m: str = context.message.content.split(' ')

        # Parse for data
        try: name, message, got = args[1], ' '.join(m[3:]), True
        except: got = False

        # All data was not included
        if not got: return await context.send(config.X_EMOJI + " Must specify a name for the tag")

        # See if the tag exists
        failed = True
        try: TagItem(name)
        except: failed = False

        # The tag exists
        if failed: return await context.send(config.X_EMOJI + f" Tag `{name}` already exists")

        # Must have a value/message
        if not message:
            return await context.send(config.X_EMOJI + f" Tags must have a value!")

        # Write the tag
        TagItem.write_tag(
            name,
            message,
            context.author.id,
            False
        )

        await context.send(config.CHECK_EMOJI + f" Created `{name}` tag!")

    @commands.command()
    async def remove_tag(self, context, *args):
        try: tag: TagItem = TagItem(args[1])
        except: return await context.send(config.X_EMOJI + f" Tag `{args[1]}` does not exist!")

        TagItem.remove_tag(args[1])
        await context.send(config.CHECK_EMOJI + f" Removed tag `{args[1]}`... Value: \n```{tag.message}```")

    @commands.command()
    async def list_tags(self, context, *args):
        names = [tag.name for tag in TagItem.get_tags()]
        strings = [f"• `{name}`" for name in names]

        eb = discord.Embed(
            title="Tags List (All Tags)",
            description='\n'.join(strings),
            colour=config.EMBED_COLOUR_STRD
        )

        await context.send(embed=eb)


def setup(bot):
    bot.add_cog(Tags(bot))
