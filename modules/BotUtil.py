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
                async with session.get(config.TopicChannels.EXTENSION_URL) as request:
                    try:
                        data = await request.json()
                        return data["value"]
                    except Exception as ex:
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
    async def get_chromegle_count():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config.CounterChannels.CHROMEGLE_STATS_URL) as request:
                    try:
                        response = await request.json()
                        return response["payload"].get("online_users")
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
