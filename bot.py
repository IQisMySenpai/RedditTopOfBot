import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('ODQxNzc3Njg2OTU4MzA5NDQ2.YJrskA.XBbTbMxdZVSPzONfUD1_lVfku_o')

client = discord.Client()

# Add Code Here

client.run(TOKEN)