from datetime import datetime

BOT_PREFIX = "!"
COG_PATH = "./cogs"
DATA_PATH = "./resources/data.json"
BOT_ADMINS = [699802828356583435, 164788187296694274, 600913266394529813]

# Custom Emojis
CHECK_EMOJI: str = "<:check:655594481789173790>"
X_EMOJI: str = "<:xmark:655594482070454300>"

# Embed Colour Codes (Styling)
EMBED_COLOUR_STRD: hex = 0x483b99  # Old: 0xc2364e
EMBED_COLOUR_ERROR: hex = 0xf03f32
EMBED_COLOUR_SUCCESS: hex = 0x3ec966
EMBED_COLOUR_LOGS: hex = 0x6be2f2
EMBED_COLOUR_GOLD: hex = 0xd97f02

# Auto Support Message
HOME_GUILD_ID: int = 798632874776985660
AUTO_MESSAGE_CHANNEL: int = 869399747243421716

OWNER_ID: int = 699802828356583435

EXTENSION_URL: str = "https://chrome.google.com/webstore/detail/chromegle-full-omegle-cli/gcbbaikjfjmidabapdnebofcmconhdbn?hl=en"

TOPIC_CHANNELS: list = [
    (869399708865560608, "Download Chromegle today to join **[%users% other users]** re-inventing the experience forever!"),
    (869399671402004480, "**[Click Me!] - [https://github.com/isaackogan/Chromegle]** - Chromegle client update news and information"),
    (869399602829336576, "**[Statistics: %users% Users]** - Got a question? We might have an answer. If not, go ahead and ask in <#869399747243421716>."),
    (869399747243421716, "**[Statistics: %users% Users]** - Need support? Can't figure something out? We'd love to try and help you out.")
]
TOPIC_STRING: str = "%users%"

CONTENT_CREATOR_ROLE: int = 823974449958354964
LIVE_CREATOR_ROLE: int = 869681524277145650
