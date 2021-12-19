from dataclasses import dataclass
from typing import Tuple, List

BOT_PREFIX = "!"
COG_PATH = "./cogs"
DATA_PATH = "./resources/data.json"
BOT_ADMINS = [699802828356583435, 164788187296694274]

# Custom Emojis
CHECK_EMOJI: str = "<:check:655594481789173790>"
X_EMOJI: str = "<:xmark:655594482070454300>"

# Embed Colour Codes (Styling)
EMBED_COLOUR_STRD: hex = 0x189ed8  # Old: 0xc2364e
EMBED_COLOUR_ERROR: hex = 0xf03f32
EMBED_COLOUR_SUCCESS: hex = 0x3ec966
EMBED_COLOUR_LOGS: hex = 0x6be2f2
EMBED_COLOUR_GOLD: hex = 0xd97f02

# Auto Support Message
HOME_GUILD_ID: int = 922231395605159987
AUTO_MESSAGE_CHANNEL: int = 922237219404673104
BOT_OWNER_ID: int = 699802828356583435


class TopicChannels:
    EXTENSION_URL: str = "https://chrome.google.com/webstore/detail/chromegle-omegle-ip-pulle/gcbbaikjfjmidabapdnebofcmconhdbn?hl=en"
    TOPIC_STRING: str = "%users%"

    TOPIC_CHANNELS: List[Tuple[int, str]] = [
        (922237065222029352, "Download Chromegle today to join **[%users% other users]** re-inventing the experience forever!"),
        (922234489336377385, "**[Click Me!] - [https://github.com/ChromegleApp/Chromegle]** - Chromegle client update news and information"),
        (922234591538987049, "**[Click Me!] - [https://github.com/ChromegleApp/Chromegle]** - Chromegle client update news and information"),
        (922237064215412816, "**[Statistics: %users% Users]** - Got a question? We might have an answer. If not, go ahead and ask in <#922237219404673104>."),
        (922237219404673104, "**[Statistics: %users% Users]** - Need support? Can't figure something out? We'd love to try and help you out.")
    ]


@dataclass
class CounterChannels:
    COUNT_STRING: str = "%count%"

    MEMBER_COUNT_CHANNEL_ID: int = 922234989452615741
    USER_COUNT_CHANNEL_ID: int = 922235111708164127

    MEMBER_COUNT_MESSAGE: str = "Discord Members: %count%"
    USER_COUNT_MESSAGE: str = "App Users: %count%"
