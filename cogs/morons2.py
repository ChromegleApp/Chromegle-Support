import discord
from discord.ext import commands

# Define the role IDs that are allowed to use the commands
allowed_role_ids = [1079276953602891826, 922249784012709920]

# Define the role ID for the "morons" role
role_id = 1065385186130411562  # Replace with the actual role ID

class MoronsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def morons(self, ctx, member: discord.Member = None):
        # Check if the command sender has one of the allowed roles
        if any(role.id in allowed_role_ids for role in ctx.author.roles):
            if member is None:
                await ctx.send("Please specify a user to assign the 'morons' role to.")
                return

            # Get the role object using the role ID
            role = ctx.guild.get_role(role_id)

            # Check if the role exists
            if role is not None:
                # Add the role to the specified member
                await member.add_roles(role)
                await ctx.send(f"Role {role.name} added to {member.mention}")
            else:
                await ctx.send("The specified role does not exist.")
        else:
            await ctx.send("You must have one of the allowed roles to use this command.")

    @commands.command()
    async def unmorons(self, ctx, member: discord.Member = None):
        # Check if the command sender has one of the allowed roles
        if any(role.id in allowed_role_ids for role in ctx.author.roles):
            if member is None:
                await ctx.send("Please specify a user to remove the 'morons' role from.")
                return

            # Get the role object using the role ID
            role = ctx.guild.get_role(role_id)

            # Check if the role exists
            if role is not None:
                # Remove the role from the specified member
                await member.remove_roles(role)
                await ctx.send(f"Role {role.name} removed from {member.mention}")
            else:
                await ctx.send("The specified role does not exist.")
        else:
            await ctx.send("You must have one of the allowed roles to use this command.")

def setup(bot):
    bot.add_cog(MoronsCog(bot))