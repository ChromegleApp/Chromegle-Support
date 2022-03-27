from io import BytesIO

import aiohttp
import discord
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from discord import Member

import config


def reformat_number(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


def mask_circle_transparent(original: Image, blur_radius: int, offset: int = 0) -> Image:
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


async def get_profile_picture(url: str) -> Image:
    """
    Process Avatar URL into circular thumbnail image

    :param url: Avatar URL
    :return: Processed PIL Image

    """

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as request:
            with BytesIO(await request.read()) as stream:
                image = Image.open(stream).resize((256, 256)).convert("RGBA")
                return mask_circle_transparent(image, 5)


def generate_welcome_embed(member: Member) -> discord.Embed:
    """
    Create welcome embed that is personalized to each user

    :param member:
    :return:

    """
    return discord.Embed(
        description=config.Welcome.EMBED_DESCRIPTION,
        colour=config.Welcome.JOIN_COLOUR
    ).set_thumbnail(url="attachment://ProfilePicture.png")


async def create_card(user, achieved_xp, needed_xp, rank, level):
    status = str(user.status)
    name = user.name
    discriminator = user.discriminator
    pfp_url = str(user.avatar_url_as(format="png"))

    # DIMENSIONS
    image_width, image_height = 800, 200
    pfp_dimensions = round(image_height / 1.05)

    # Fonts
    header_font = ImageFont.truetype('./resources/card_resources/card_font.ttf', 32)
    large_font = ImageFont.truetype('./resources/card_resources/card_font.ttf', 45)
    small_font = ImageFont.truetype('./resources/card_resources/card_font.ttf', 22)

    # Setting Up the Image
    img = Image.new('RGBA', (image_width, image_height))
    draw = ImageDraw.Draw(img)

    pfp = await get_profile_picture(pfp_url)
    pfp.thumbnail((pfp_dimensions, pfp_dimensions))

    # Drawing Profile Picture & Border
    pfp_offset = ((image_height // 2) - pfp_dimensions // 2)
    img.paste(pfp, (pfp_offset - 9, pfp_offset - 8))  # Drawing the profile picture mask=pfp

    achieved_xp = max(0, achieved_xp)
    needed_xp = max(1, needed_xp)

    # Drawing the progress bar
    progress_bar_width, progress_bar_height = round((image_width / 1.45)), round((image_height / 6))
    progress_bar_location = ((round(image_width - image_width / 1.38)), (round(image_height - image_height / 3.4)))

    draw.rectangle(((progress_bar_location[0], progress_bar_location[1]), (progress_bar_width + progress_bar_location[0], progress_bar_height + progress_bar_location[1])), fill=config.LevelSystem.RankCard.CARD_PROGRESS)

    if achieved_xp > 0:
        draw.rectangle(((progress_bar_location[0], progress_bar_location[1]), (round(progress_bar_location[0] + ((achieved_xp / needed_xp) * progress_bar_width))), progress_bar_height + progress_bar_location[1]),
                       fill=config.LevelSystem.RankCard.CARD_PRIMARY)

    # Drawing the Discord Name & Discriminator
    if len(name) > 15:
        discord_name = name[:15]
    else:
        discord_name = name
    discord_discriminator = f"#{discriminator}"

    discord_name_length = header_font.getsize(discord_name)[0]

    draw.text((progress_bar_location[0] + 15, progress_bar_location[1] - 45), discord_name, font=header_font, fill=config.LevelSystem.RankCard.CARD_SECONDARY)
    draw.text((progress_bar_location[0] + 25 + discord_name_length, progress_bar_location[1] - 35), discord_discriminator, font=small_font, fill=config.LevelSystem.RankCard.CARD_TERTIARY)

    # Drawing the User's XP
    achieved_xp_formatted = reformat_number(achieved_xp)
    achieved_xp_length = small_font.getsize(achieved_xp_formatted)[0]

    needed_xp_formatted = f"/ {reformat_number(needed_xp)} XP"
    needed_xp_length = small_font.getsize(needed_xp_formatted)[0]
    needed_xp_location = (progress_bar_width + progress_bar_location[0] - needed_xp_length, progress_bar_location[1] - 35)

    draw.text(needed_xp_location, needed_xp_formatted, font=small_font, fill=config.LevelSystem.RankCard.CARD_TERTIARY)
    draw.text((needed_xp_location[0] - achieved_xp_length - 9, needed_xp_location[1]), achieved_xp_formatted, font=small_font, fill=config.LevelSystem.RankCard.CARD_SECONDARY)

    # Drawing the User's Level
    level_length = large_font.getsize(str(level))[0]
    level_location = (progress_bar_width + progress_bar_location[0] - level_length, 8)

    level_label_location = (level_location[0] - small_font.getsize("LEVEL")[0] - 10, 28)

    draw.text(level_label_location, "LEVEL", font=small_font, fill=config.LevelSystem.RankCard.CARD_PRIMARY)
    draw.text(level_location, str(level), font=large_font, fill=config.LevelSystem.RankCard.CARD_PRIMARY)

    # Drawing the User's Rank
    if rank is not None:
        rank_formatted = f"#{rank}"
        rank_formatted_length = large_font.getsize(rank_formatted)[0]
        rank_formatted_location = (level_label_location[0] - rank_formatted_length - 10, level_location[1])
        draw.text(rank_formatted_location, rank_formatted, font=large_font, fill=config.LevelSystem.RankCard.CARD_SECONDARY)

        rank_label_location = (rank_formatted_location[0] - small_font.getsize("RANK")[0] - 10, level_label_location[1])
        draw.text(rank_label_location, "RANK", font=small_font, fill=config.LevelSystem.RankCard.CARD_SECONDARY)

    backing_width = round(image_width * 1.05)
    backing_height = round(image_height * 1.3)

    async with aiohttp.ClientSession() as session:
        async with session.get(config.LevelSystem.RankCard.CARD_BACKGROUND_URL) as request:
            with BytesIO(await request.read()) as stream:
                backing_img = Image.open(stream).resize((backing_width, backing_height)).convert("RGBA")

    backing_img.paste(img, (20, 28), img)

    return backing_img
