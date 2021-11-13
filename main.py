import discord 
from discord.ext import commands
from discord_slash import SlashCommand
from utils import RollProcess, guildIDs
from discord_slash.utils.manage_commands import create_option, create_choice
from utils import MakeAccount

bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} in {len(bot.guilds)} guilds.")
    for user in bot.users:
        if not user.bot:
            await MakeAccount(user).makeAccount()

bot.load_extension("cogs.levelup")
bot.load_extension("cogs.roll")
bot.load_extension("cogs.makeaccount")
bot.load_extension("cogs.cards")
bot.run("TOKEN GOES HERE")