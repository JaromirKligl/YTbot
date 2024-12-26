import os
import discord
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
import pathlib


import images
import songs

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup intents
intents = Intents.default()
intents.message_content = True

# Bot instance
bot = commands.Bot(command_prefix='%', intents=intents)

images.setup(bot)
songs.setup(bot)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command()
async def matfyz(ctx):
    """Skibidi gyat"""
    file_path = pathlib.Path.cwd() /"fyz.png"
    await ctx.send(file=discord.File(file_path))


@bot.command()
async def rouz(ctx):
    """the xd moment"""
    file_path = pathlib.Path.cwd() /"rouz.jpg"
    await ctx.send(file=discord.File(file_path))



def main():
    bot.run(TOKEN)


if __name__ == '__main__':
    main()