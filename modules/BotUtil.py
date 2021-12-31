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

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config.TopicChannels.EXTENSION_URL, proxy=open("./resources/bot_proxy.txt", "r").read()) as request:
                    try:
                        html = await request.text()
                        return html.split('users">')[1].split("</span")[0].split(" ")[0]
                    except:
                        logging.error(traceback.format_exc())
                        return None
        except:
            logging.error(traceback.format_exc())
            return None

    @staticmethod
    async def get_omegle_count():

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config.CounterChannels.OMEGLE_STATS_URL) as request:
                    try:
                        response = await request.json()
                        return response["payload"]["count"]
                    except:
                        logging.error(traceback.format_exc())
                        return None
        except:
            logging.error(traceback.format_exc())
            return None

    @staticmethod
    def reduce_granularity(x: float, n: int = 2):
        _x = str(x)
        return int(_x[:n] + "0" * (len(_x) - n))
