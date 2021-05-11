import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('ODQxNzc3Njg2OTU4MzA5NDQ2.YJrskA.XBbTbMxdZVSPzONfUD1_lVfku_o')

client = discord.Client()

bot = commands.Bot(command_prefix='$')

@bot.command()
async def postrepeat(ctx, subreddit="r/ProgrammerHumor", freqhours: int = 24, topof="week"):
    

    response = "Test"
    await ctx.send(response)

client.run(TOKEN)