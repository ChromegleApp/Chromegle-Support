import discord
import dislash
from discord import MessageType
from discord.ext import commands
from discord.ext.commands import BucketType
from dislash import ContextMenuInteraction, CommandOnCooldown

import config
from bot import ChromegleSupport, inter_client


class AutoChannels(commands.Cog):

    def __init__(self, bot: ChromegleSupport):
        self.bot = bot

    @inter_client.message_command(name="Pin Message", guild_ids=[config.HOME_GUILD_ID])
    @dislash.cooldown(3, 3600, type=BucketType.user)
    async def pin(self, interaction: ContextMenuInteraction):
        # Has message perms
        if not interaction.author.permissions_in(interaction.message.channel).send_messages:
            await interaction.reply(
                embed=discord.Embed(
                    description=f"{config.X_EMOJI} You cannot pin messages in {interaction.message.channel.mention}",
                    colour=config.EMBED_COLOUR_ERROR
                ).set_author(
                    name=str(interaction.author), icon_url=interaction.author.avatar_url),
                ephemeral=True
            )
            return

        # Is a regular message
        if (interaction.message.type != MessageType.default):
            await interaction.reply(
                embed=discord.Embed(
                    description=f"{config.X_EMOJI} You cannot pin messages of this type.",
                    colour=config.EMBED_COLOUR_ERROR
                ).set_author(
                    name=str(interaction.author), icon_url=interaction.author.avatar_url),
                ephemeral=True
            )
            return

        # Already Pinned
        if (interaction.message.pinned):
            await interaction.reply(
                embed=discord.Embed(
                    description=f"{config.X_EMOJI} That message is already pinned!",
                    colour=config.EMBED_COLOUR_ERROR
                ).set_author(
                    name=str(interaction.author), icon_url=interaction.author.avatar_url),
                ephemeral=True
            )
            return

        # Max number of pins
        if len(await interaction.channel.pins()) >= 50:
            await interaction.reply(
                embed=discord.Embed(
                    description=f"{config.X_EMOJI} This channel is at the maximum number of pins.",
                    colour=config.EMBED_COLOUR_ERROR
                ).set_author(
                    name=str(interaction.author), icon_url=interaction.author.avatar_url),
                ephemeral=True
            )
            return

        # Pin Message
        await interaction.reply(
            embed=discord.Embed(
                description=(
                    f"{config.CHECK_EMOJI} Successfully pinned message from `{str(interaction.message.author).replace('`', '')}` "
                    f"in {interaction.message.channel.mention}"
                ),
                colour=config.EMBED_COLOUR_STRD
            ).set_author(
                name=str(interaction.author), icon_url=interaction.author.avatar_url)
        )
        await interaction.message.pin()

    @inter_client.message_command(name="Unpin Message", guild_ids=[config.HOME_GUILD_ID])
    @dislash.cooldown(1, 3600, type=BucketType.user)
    async def unpin(self, interaction: ContextMenuInteraction):
        # Has message perms
        if not interaction.author.permissions_in(interaction.message.channel).send_messages:
            await interaction.reply(
                embed=discord.Embed(
                    description=f"{config.X_EMOJI} You cannot pin messages in {interaction.message.channel.mention}",
                    colour=config.EMBED_COLOUR_ERROR
                ).set_author(
                    name=str(interaction.author), icon_url=interaction.author.avatar_url),
                ephemeral=True
            )
            return

        # Not Pinned
        if (not interaction.message.pinned):
            await interaction.reply(
                embed=discord.Embed(
                    description=f"{config.X_EMOJI} That message is not currently pinned!",
                    colour=config.EMBED_COLOUR_ERROR
                ).set_author(
                    name=str(interaction.author), icon_url=interaction.author.avatar_url),
                ephemeral=True
            )
            return

        # Unpin Message
        await interaction.reply(
            embed=discord.Embed(
                description=(
                    f"{config.CHECK_EMOJI} Successfully unpinned message from `{str(interaction.message.author).replace('`', '')}` "
                    f"in {interaction.message.channel.mention}"
                ),
                colour=config.EMBED_COLOUR_STRD
            ).set_author(
                name=str(interaction.author), icon_url=interaction.author.avatar_url)
        )
        await interaction.message.unpin()

    @pin.error
    @unpin.error
    async def on_error(self, context, error):
        if type(error) == CommandOnCooldown:
            e: list = str(error).split("Try again in ")
            e[1] = f"Try again in `{e[1]}`"

            await context.reply(
                embed=discord.Embed(
                    description=f"{config.X_EMOJI} {' '.join(e)}!",
                    colour=config.EMBED_COLOUR_ERROR
                ).set_author(
                    name=str(context.author), icon_url=context.author.avatar_url),
                ephemeral=True
            )
            return

        raise error


def setup(bot):
    bot.add_cog(AutoChannels(bot))
