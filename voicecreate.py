import discord
from discord.ext import commands
import traceback
import os
import sys
import asyncio

intents=discord.Intents.all()
bot = commands.Bot(command_prefix=".",intents=intents)

bot.remove_command("help")


initial_extensions = ['cogs.voice',]


async def main():
    async with bot:
        for extension in initial_extensions:
            try:
                await bot.load_extension(extension)
                print(extension,"loaded")
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()
        await bot.start(os.environ["BOT_TOkEN"])


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

if __name__ == '__main__':
    asyncio.run(main())
