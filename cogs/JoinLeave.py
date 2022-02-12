import asyncio
from io import BytesIO
from typing import Optional

import aiohttp
import discord
from PIL import Image, ImageDraw, ImageFilter
from discord import TextChannel, Member
from discord.ext import commands
from discord.ext.commands import Bot

import config


class JoinLeave(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.channel: Optional[TextChannel] = None

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Load the channel on bot ready
        :return: None

        """
        self.channel: TextChannel = await self.bot.fetch_channel(config.JoinLeave.MESSAGE_CHANNEL_ID)

    @staticmethod
    def __mask_circle_transparent(original: Image, blur_radius: int, offset: int = 0) -> Image:
        """
        Crop image into circle with a transparent background
        Via https://note.nkmk.me/en/python-pillow-square-circle-thumbnail/

        :param original: Image to crop
        :param blur_radius: Radius for blur (intensity)
        :param offset: Image offset
        :return: New Image

        """
        offset += blur_radius * 2
        mask = Image.new("L", original.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((offset, offset, original.size[0] - offset, original.size[1] - offset), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

        result = original.copy()
        result.putalpha(mask)

        return result

    @staticmethod
    async def __get_profile_picture(url: str) -> Image:
        """
        Process Avatar URL into circular thumbnail image

        :param url: Avatar URL
        :return: Processed PIL Image

        """

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as request:
                with BytesIO(await request.read()) as stream:
                    image = Image.open(stream).resize((256, 256)).convert("RGBA")
                    return JoinLeave.__mask_circle_transparent(image, 5)

    @staticmethod
    def __generate_welcome_embed(member: Member) -> discord.Embed:
        """
        Create welcome embed that is personalized to each user

        :param member:
        :return:

        """
        return discord.Embed(
            title=f":wave: Welcome, `{str(member).replace('`', '')}`",
            colour=config.JoinLeave.JOIN_COLOUR
        ).set_thumbnail(url="attachment://ProfilePicture.png")

    @staticmethod
    def __generate_goodbye_embed(member: Member) -> discord.Embed:
        """
        Create goodbye embed that is personalized to each user

        :param member:
        :return:

        """
        return discord.Embed(
            title=f":dove: Goodbye, `{str(member).replace('`', '')}`",
            colour=config.JoinLeave.LEAVE_COLOUR
        ).set_thumbnail(url="attachment://ProfilePicture.png")

    async def __send_join_leave_message(self, is_join: True, member: Member):
        """
        Send the join or leave message based on is_join parameter

        :param is_join: Whether or not they joined (if false, they left)
        :return: None

        """

        image: Image = await self.__get_profile_picture(str(member.avatar_url))

        buffer = BytesIO()
        image.save(buffer, "png")
        buffer.seek(0)

        # Give it a chance to load up
        if self.channel is None:
            await asyncio.sleep(5)
            if self.channel is None:
                return

        await self.channel.send(
            file=discord.File(buffer, filename="ProfilePicture.png"),
            embed=self.__generate_welcome_embed(member) if is_join else self.__generate_goodbye_embed(member)
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        if int(member.guild.id) != config.HOME_GUILD_ID:
            return

        await self.__send_join_leave_message(is_join=True, member=member)

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        if int(member.guild.id) != config.HOME_GUILD_ID:
            return

        await self.__send_join_leave_message(is_join=False, member=member)


def setup(bot):
    bot.add_cog(JoinLeave(bot))
