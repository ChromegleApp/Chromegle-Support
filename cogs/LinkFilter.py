import logging
import re
import traceback
from typing import List, Optional, Tuple

from discord import Message
from discord.ext import commands

import config


class LinkFilterModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.whitelist_fp = config.LinkFilter.WHITELIST_PATH
        self.whitelist = self.__load_whitelist_words()

    def __load_whitelist_words(self) -> List[str]:
        """
        Load the whitelist from a newline delimited text file
        :return: None

        """

        try:
            raw_text: str = open(self.whitelist_fp, 'r').read()
            return [url.strip() for url in raw_text.split("\n")]
        except:
            logging.error(traceback.format_exc())
            return []

    @staticmethod
    def capture_url_groups(word: str):
        """
        Get all instances of URLs in a word

        :param word: The word
        :return: List of all URL instances

        """

        url_regex = re.compile(
            (
                "((?:(?<=[^a-zA-Z0-9]){0,}"
                "(?:(?:https?://){0,1}(?:[a-zA-Z0-9%]"
                "{1,}:[a-zA-Z0-9%]{1,}[@]){,1})"
                "(?:(?:\w{1,}\.{1}){1,5}(?:(?:[a-zA-Z]){1,})|"
                "(?:[a-zA-Z]{1,}\/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]"
                "{1,3}\.[0-9]{1,3}\:[0-9]{1,4}){1})){1}(?:(?:"
                "(?:\/{0,1}(?:[a-zA-Z0-9\-_=-]){1,})*)"
                "(?:[?][a-zA-Z0-9\=\%\&\_\-]{1,}){0,1})"
                "(?:\.(?:[a-zA-Z0-9]){0,}){0,1})"
            ), re.IGNORECASE)

        match: Optional[re.Match] = url_regex.match(word)

        if match is None:
            return []

        # check length of the url's TLD
        check2 = len(match.group().split(".")[-1])

        # TLDs from ICANN are minimum of 2 letters, therefore this must be an acronym and not a URL
        if check2 < 2:
            return []

        return list(match.groups())

    def word_contains_unwhitelisted_url(self, word: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a given word contains an unwhitelisted URL by checking if it's a URL and recursively
        re-checking if a whitelisted group is found.

        :param word:
        :return:
        """
        offences: List[str] = self.capture_url_groups(word.strip())

        # No offences
        if len(offences) == 0:
            return False, None

        # Possible offence, must verify
        for offence in offences:
            # Replace protocol w/ nothing
            offence = re.sub("https://|http://|ftp://|localhost://", "", offence, flags=re.IGNORECASE)

            try:
                offence = offence.split("/")[0]
            except IndexError:
                pass

            # Check if remaining URL is whitelisted. If not, throw True
            if not any(offence in word for word in self.whitelist):
                return True, offence

        # Otherwise false
        return False, None

    def phrase_contains_unwhitelisted_url(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a phrase (string) contains an unwhitelisted URL
        :param content: Content of message
        :return: True or false test result

        """
        words: List[str] = content.replace("\n", " ").replace("\t", " ").replace("@everyone", " ").replace("@here", " ").replace("-", "").split(" ")

        for word in words:
            offence, value = self.word_contains_unwhitelisted_url(word)

            if offence:
                return True, value

        return False, None

    @commands.Cog.listener()
    async def on_message(self, message: Message):

        if (
                message.author.bot
                or not message.guild
                or (int(message.guild.id) != config.HOME_GUILD_ID)
                or (any([int(role.id) in config.LinkFilter.IGNORED_ROLES for role in message.author.roles]))
        ):
            return

        violation, value = self.phrase_contains_unwhitelisted_url(str(message.content).lower())

        if not violation:
            return

            # Attempt to delete the message
        try:
            await message.delete()
        except:
            pass

        # Attempt to send them a warning message
        if config.LinkFilter.SEND_WARNING_DM:
            try:
                channel = await message.author.create_dm()
                await channel.send(config.LinkFilter.WARNING_MESSAGE % value)
            except:
                pass


def setup(bot):
    bot.add_cog(LinkFilterModule(bot))
