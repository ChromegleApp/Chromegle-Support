from typing import Tuple, List

BOT_PREFIX = "!"
COG_PATH = "./cogs"
DATA_PATH = "./resources/data.json"
BOT_ADMINS = [699802828356583435, 164788187296694274, 303212283327283202, 927114260545429565]

# Custom Emojis
CHECK_EMOJI: str = "<:check:655594481789173790>"
X_EMOJI: str = "<:xmark:655594482070454300>"

# Embed Colour Codes (Styling)
EMBED_COLOUR_STRD: hex = 0x189ed8  # Old: 0xc2364e
EMBED_COLOUR_ERROR: hex = 0xf03f32
EMBED_COLOUR_SUCCESS: hex = 0x3ec966
EMBED_COLOUR_LOGS: hex = 0x6be2f2
EMBED_COLOUR_GOLD: hex = 0xd97f02
EMBED_COLOUR_INVIS: hex = 0x2f3136

# Auto Support Message
HOME_GUILD_ID: int = 922231395605159987
AUTO_MESSAGE_CHANNEL: int = 922237219404673104
BOT_OWNER_ID: int = 699802828356583435


class TopicChannels:
    EXTENSION_URL: str = "https://img.shields.io/chrome-web-store/users/gcbbaikjfjmidabapdnebofcmconhdbn.json"
    TOPIC_STRING: str = "%users%"

    TOPIC_CHANNELS: List[Tuple[int, str]] = [
        (922237065222029352, "Download Chromegle today to join **[%users% other users]** re-inventing the experience forever!"),
        (922234489336377385, "**[Click Me!] - [https://github.com/ChromegleApp/Chromegle]** - Chromegle client update news and information"),
        (922234591538987049, "**[Click Me!] - [https://github.com/ChromegleApp/Chromegle]** - Chromegle client update news and information"),
        (922237064215412816, "**[Statistics: %users% Users]** - Got a question? We might have an answer. If not, go ahead and ask in <#922237219404673104>."),
        (922234839233609849, "**[Statistics: %users% Users]** - Need support? Can't figure something out? We'd love to try and help you out.")
    ]


class CounterChannels:
    COUNT_STRING: str = "%count%"

    MEMBER_COUNT_CHANNEL_ID: int = 922234989452615741
    USER_COUNT_CHANNEL_ID: int = 922235111708164127
    OMEGLE_COUNT_CHANNEL_ID: int = 926334350100951091

    OMEGLE_COUNT_MESSAGE: str = "Omegle Users: %count%"
    MEMBER_COUNT_MESSAGE: str = "Discord Members: %count%"
    USER_COUNT_MESSAGE: str = "Downloads: %count%"
    ONLINE_COUNT_MESSAGE: str = "%count% Online on App"

    OMEGLE_STATS_URL: str = "https://chromegle.isaackogan.com/omegle/stats"
    CHROMEGLE_STATS_URL: str = "https://chromegle.isaackogan.com/chromegle/stats"


class JoinLeave:
    MESSAGE_CHANNEL_ID: int = 925620656547172452
    JOIN_COLOUR: hex = 0x3bb879
    LEAVE_COLOUR: hex = 0xd9092f

class BrandInfo:
    ANIMATED_LOGO: str = "https://i.imgur.com/PhrQgql.png"


class LinkFilter:
    """
    Configuration for the URL filter

    """

    WHITELIST_PATH: str = "./resources/url_whitelist.txt"
    SEND_WARNING_DM: bool = True
    WARNING_MESSAGE: str = "Please **do not send links** to the Chromegle discord server! You sent `%s`. Thank you for your co-operation. :slight_smile:"

    IGNORED_ROLES = [
        922295829950238751,  # Bots disguised as humans
        922249784012709920,  # Admin
        928873845992063047,  # Family
    ]


class NSFWTesting:
    """
    NSFW Message Testing

    """
    TEST_CHANNEL_ID: int = 953113489772261396


class LevelSystem:
    DB_PATH: str = "./resources/levels/level_system.db"
    JSON_PATH: str = "./resources/levels/level_system.json"

    MIN_ADD_XP: int = 0
    MAX_ADD_XP: int = 10

    LEADERBOARD_WEEKLY: str = "leaderboard_weekly"
    LEADERBOARD_MONTHLY: str = "leaderboard_monthly"
    LEADERBOARD_FOREVER: str = "leaderboard_forever"
    MEMBER_OF_THE_WEEK_ROLE: int = 957764178406412318
    MAIN_CHAT_CHANNEL: int = 922234839233609849

    BLACKLISTED_CHANNELS: List[int] = [
        953113489772261396
    ]

    BOT_COMMANDS_CHANNEL: int = 922234877984792686

    LEVEL_ROLES: dict = {
        1: 957764734625677393,
        5: 957764707140386856,
        10: 957764695832526910,
        20: 957764665545461860,
        30: 957764663867748372,
        40: 957764551389098004,
        50: 957764549921083453,
        60: 957764549220634724,
        70: 957764548218220574,
        80: 957764546062319666,
        90: 957764538810392688,
        100: 957764492501061682
    }

    class ActivityRoles:
        ACTIVITY_ROLES: dict = {
            500: 957768323557388330,
            2500: 957768354595242066
        }

    class ChannelBoards:
        EMOJIS: dict = {
            1: "1st:957769795347046401",
            2: "2nd:957769795464466494",
            3: "3rd:957769795653222400",
            4: "4th:957769795963613204",
            5: "5th:957769795833569330",
            6: "6th:957769795690987539",
            7: "7th:957769795699355688",
            8: "8th:957769795917479987",
            9: "9th:957769795355435059",
            10: "10th:957769795674193930",
            "xp": "xp:957771518614593566",
            "lb_crown": "a:lb_crown:957771393230053426"
        }
        BOARD_CHANNEL: int = 957768628487483392
        UPDATE_MINUTES: int = 5

    class Leaderboard:
        LIMIT_USERS: int = 1500
        RESULTS_PER_PAGE: int = 9

    class RankCard:
        CARD_BACKGROUND_URL = "https://i.imgur.com/5uL3TN7.png?1"

        CARD_PRIMARY = 232, 100, 100
        CARD_PROGRESS = (72, 75, 78)
        CARD_SECONDARY = (255, 255, 255)
        CARD_TERTIARY = (255, 255, 255)
