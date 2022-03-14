import discord
from discord import Member, Role
from discord.ext import commands
from discord_components import Button, ButtonStyle
from dislash import MessageInteraction

import config


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.labels = [
            {
                'label': 'Chromegle Updates',
                'emoji': '🌎',
                'role_id': 923399789427695658
            },
            {
                'label': 'OmeglePy Updates',
                'emoji': '📚',
                'role_id': 923399875465457684
            }
        ]
        self.guild = None

    @commands.command()
    async def rmenu(self, context):
        if not int(context.author.id) in config.BOT_ADMINS:
            return

        eb = discord.Embed(
            title="Chromegle Self-Assigned Roles",
            colour=config.EMBED_COLOUR_STRD
        )

        eb.add_field(
            name="_ _\nI'm here for Chromegle",
            value=(
                "React with 🌎 to receive the role `Chromegle Updates`\n\n"
                "People who want access to changelogs/updates for the Chromegle app."
                "\n\n_ _"
            ),
            inline=False
        )

        eb.add_field(
            name="I'm here for OmeglePy",
            value=(
                "React with 📚 to receive the role `OmeglePy Updates`\n\n"
                "People who want access to changelogs/updates for the Chromegle app."
                "\n\n_ _"
            ),
            inline=False
        )

        await context.send(
            embed=eb,
            components=[
                [
                    Button(style=ButtonStyle.gray, label=self.labels[0]['label'], emoji=self.labels[0]['emoji']),
                    Button(style=ButtonStyle.gray, label=self.labels[1]['label'], emoji=self.labels[1]['emoji'])
                ]
            ]
        )

    @commands.Cog.listener()
    async def on_button_click(self, res: MessageInteraction):
        try:
            await res.respond(type=6)
        except:
            pass

        # Must be in a guild
        if res.guild is None:
            return

        member: Member = await res.guild.fetch_member(res.author.id)

        # For each item
        for item in self.labels:
            # If they clicked the item
            if res.component.label == item['label']:
                # Get the role
                role: Role = res.guild.get_role(item['role_id'])

                # If they have the role
                if role in member.roles:
                    await member.remove_roles(role)
                    await self.send_dm(res.author, f"Removed role `{role.name}`")
                else:
                    await self.send_dm(res.author, f"Added role `{role.name}`")
                    await member.add_roles(role)

    @staticmethod
    async def send_dm(member: Member, message: str):
        try:
            channel = await member.create_dm()
            await channel.send(message)
        except:
            pass


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
