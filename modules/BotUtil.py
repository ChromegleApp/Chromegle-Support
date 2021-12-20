import asyncio
import logging
import traceback
from datetime import datetime

import aiohttp

import config


class BotUtil:

    @staticmethod
    def time_from_unix(time: float):
        time = datetime.utcfromtimestamp(time)
        return time.strftime('%D | %I:%M %p (UTC)')

    @staticmethod
    async def get_extension_count():

        async with aiohttp.ClientSession() as session:
            async with session.get(config.TopicChannels.EXTENSION_URL, proxy=open("./resources/bot_proxy.txt", "r").read()) as request:
                try:
                    html = await request.text()
                    return html.split('users">')[1].split("</span")[0].split(" ")[0]
                except:
                    logging.error(traceback.format_exc())
                    return None

    @staticmethod
    def jsonify_member(member):

        return {
            "avatar_url": str(member.avatar_url),
            "name": member.name,
            "discriminator": member.discriminator,
            "id": member.id,
        }
