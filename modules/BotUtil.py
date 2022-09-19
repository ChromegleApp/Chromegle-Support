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
    def reduce_granularity(x: float, n: int = 2):
        _x = str(x)
        return int(_x[:n] + "0" * (len(_x) - n))
