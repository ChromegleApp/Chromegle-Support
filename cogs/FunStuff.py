from discord.ext import commands


class FunStuff(commands.Cog):

    def __int__(self, bot):
        self.bot = bot

    @commands.command(name="rock")
    async def rock(self, context):
        await context.reply("https://tenor.com/view/rock-one-eyebrow-raised-rock-staring-the-rock-gif-22113367", mention_author=False)


def setup(bot):
    bot.add_cog(FunStuff(bot))

