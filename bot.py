import os
import discord
from discord.ext import commands
from secret import TOKEN
import asyncio

bot = commands.Bot(command_prefix='$')

running = True


async def post_interval(ctx, interval: int = 24):

    response = "Test"
    while running:
        await asyncio.sleep(interval)

        print("Sending response")
        await ctx.send(response)


@bot.command(name='startRepeat')
async def start_post_repeat(ctx, subreddit: str = "r/ProgrammerHumor", freqhours: int = 24, topof: str = "week"):
    """
    Function sends the top post of a given subreddit to to a text channel.

    :param ctx: context of the command to which the bot is responding
    :param subreddit: subreddit to take post from
    :param freqhours: frequency in hours, how often a post is supposed to be sent
    :param topof: equivalent to the "top of" selector in reddit.print

    :return:
    """

    print(subreddit)
    print(freqhours)
    print(topof)

    out = bot.loop.create_task(post_interval(ctx, freqhours))
    print(f"out of create_task {out}")
    print("Created loop")
    # asyncio.run(post_interval(ctx, freqhours))


@bot.command(name='stopRepeat')
async def stop_post_repeat(ctx):
    global running
    print('Stopping Loop...')
    running = False


bot.run(TOKEN)
