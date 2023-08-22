import discord
from discord.ext import commands
import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Load data from the JSON file
def load_data():
    try:
        with open('tags.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"tags": {}, "SupportMessageID": None}

# Save data to the JSON file
def save_data(data):
    with open('tags.json', 'w') as file:
        json.dump(data, file, indent=4)

data = load_data()

def is_administrator():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

def get_embed_markdown(embed):
    embed_markdown = f"**{embed.title}**\n\n{embed.description}"
    for field in embed.fields:
        embed_markdown += f"\n\n**{field.name}**\n{field.value}"
    return embed_markdown

@bot.command(name="tag")
async def tag(ctx, tag_name: str):
    tag_name = tag_name.lower()  # Convert to lowercase
    if tag_name in data["tags"]:
        tag_info = data["tags"][tag_name]
        if tag_info["embed_bool"]:
            embed = discord.Embed(title=f"Support Tag: {tag_info['label']}", description=tag_info['message'], color=discord.Color.blue())
            await ctx.send(content=get_embed_markdown(embed))
        else:
            await ctx.send(content=tag_info["message"])
    else:
        await ctx.send(content="Support tag not found.")

@bot.command(name="add_tag")
@is_administrator()
async def add_tag(ctx, tag_name: str, *, tag_info: str):
    tag_name = tag_name.lower()  # Convert to lowercase
    if tag_name in data["tags"]:
        await ctx.send(content=f"Support tag '{tag_name}' already exists.")
    else:
        data["tags"][tag_name] = {
            "name": tag_name,
            "label": tag_name.capitalize(),
            "message": tag_info,
            "owner_id": ctx.author.id,
            "embed_bool": False,  # Modify this according to your needs
            "create_time": discord.utils.utcnow().timestamp()
        }
        save_data(data)
        await ctx.send(content=f"Support tag '{tag_name}' has been added.")

@bot.command(name="delete_tag")
@is_administrator()
async def delete_tag(ctx, tag_name: str):
    tag_name = tag_name.lower()  # Convert to lowercase
    if tag_name in data["tags"]:
        del data["tags"][tag_name]
        save_data(data)
        await ctx.send(content=f"Support tag '{tag_name}' has been deleted.")
    else:
        await ctx.send(content="Support tag not found.")

@bot.command(name="support")
async def help(ctx):
    help_text = (
        "Use the following commands:\n"
        "`!tag <tag_name>` - Display information about a support tag.\n"
        "`!add_tag <tag_name> <tag_info>` - Add a new support tag.\n"
        "`!delete_tag <tag_name>` - Delete an existing support tag.\n"
        "`!help` - Display this help message."
    )
    await ctx.send(content=get_embed_markdown(help_text))

bot.run('REDACTED')
