import os
import discord
from discord.ext import commands
from secret import TOKEN
import asyncio
import requests
import random

bot = commands.Bot(command_prefix='$')

running = False
posted_posts = []
size_limit = 60  # max of 100 from reddit API
retain_size_limit = 100  # max size of posted_posts list (may be bigger due to the tiem delay between the posts)

debugging = False


def poc(string):
    """
    Debugging Aid, Prints a string to the cli if the global variable 'debugging' is true

    :param string: string to print
    :return:
    """

    global debugging
    if debugging:
        print(string)


async def posting_loop(ctx, time_span: str = "week", subreddit: str = "ProgrammerHumor", interval: int = 86400):
    """
    Loop function that posts the top post of a given subreddit to a discord text channel.

    :param ctx: Command environment (Used to send the image href to the text channel)
    :param time_span: Reddit time interval of which to take the top posts
    :param subreddit: The name of the subreddit to take the top posts from, DON'T INCLUDE THE r/
    :param interval: time interval, how frequently the bot is supposed to send the top post to the text channel, in secs
    :return:
    """

    global posted_posts

    while running:
        response = await get_first_img_url(ctx, f"https://www.reddit.com/r/{subreddit}/top/.json?t={time_span}&limit={size_limit}")

        await ctx.send(response)
        await asyncio.sleep(interval)


async def get_first_img_url(ctx, href: str = f"https://www.reddit.com/r/funny/top/.json?t=hour&limit={size_limit}"):
    """
    Given a url, the function locates all the images by searching for post_hint == "image". For all found images, the
    function checks if the post is already in the list containing the already posted links. It then selects the first
    image that wasn't already posted and returns it.
    If all posts were already posted it deletes the stored posts and starts over.

    :param ctx: Command environment (Used to send to send errors)
    :param href: complete href for a valid call to the reddit api for a json, example
        https://www.reddit.com/r/funny/top/.json?t=hour&limit=60

    :return: Either the href to a image or the http error code
    """
    global posted_posts
    global retain_size_limit
    response = ""
    img_urls = []

    answer = requests.get(href, headers={'User-agent': 'RedditTopOfDiscordBot 1.0'})
    poc(f"generated href: {href}")

    if answer.status_code == 200:
        json_content = answer.json()

        for content in json_content["data"]["children"]:
            # Trying to check if post is a image, using post_hint
            # If no post_hint key is present, this post is skipped
            if "post_hint" in content["data"].keys():
                if content["data"]["post_hint"] != "image":
                    continue

            elif "is_gallery" in content["data"].keys():
                continue

            img_urls.append(content["data"]["url"])

        # checking if image is posted already
        for href in img_urls:
            if href not in posted_posts:
                response = href
                break

        # if all posts were already posted once
        if response == "":
            await ctx.send("All posts were posted already, taking first one")
            response = img_urls[0]

        # limiting size of posted_posts
        if len(posted_posts) > size_limit:
            posted_posts = posted_posts[len(posted_posts) - retain_size_limit:]

        posted_posts.append(response)
        poc(posted_posts)

        return response

    return f"Error: {answer.status_code}"


@bot.command(name='getImage', help='Retrieves a single image from a given Subreddit.')
async def get_image(ctx, subreddit: str = "funny", time_span: str = "hour"):
    """
    Function sends once the top post of a given subreddit to to a text channel.

    :param ctx: context of the command to which the bot is responding
    :param subreddit: subreddit to take post from
    :param time_span: Reddit time interval of which to take the top posts

    :return:
    """

    if time_span not in ("hour", "day", "week", "month", "year", "all"):
        await ctx.send(f"Not allowed time span\n"
                       f"You gave {time_span}, valid are (hour, day, week, month, year, all)")
        return None

    poc(subreddit)
    poc(time_span)

    response = await get_first_img_url(ctx,
                                 f"https://www.reddit.com/r/{subreddit}/top/.json?t={time_span}&limit={size_limit}")

    poc("Sending response")
    await ctx.send(response)


@bot.command(name='startRepeat', help='Starts a loop that sends the top post of a given time interval in a subreddit to the text channel.')
async def start_post_repeat(ctx, freqhours: int = 24, subreddit: str = "funny", time_span: str = "hour"):
    """
    Function starts a loop which sends the top post of a given subreddit to the discord channel.

    :param ctx: context of the command to which the bot is responding
    :param subreddit: subreddit to take post from
    :param freqhours: frequency in hours, how often a post is supposed to be sent
    :param time_span: Reddit time interval of which to take the top posts

    :return:
    """

    global running

    if time_span not in ("hour", "day", "week", "month", "year", "all"):
        await ctx.send(f"Not supported time_span, only {('hour', 'day', 'week', 'month', 'year', 'all')} supported")
        return None

    if freqhours < 1/60.0:
        await ctx.send(f"To small of a freqhours given, minimum is {1/60.0}")
        return None

    running = True

    out = bot.loop.create_task(posting_loop(ctx, time_span=time_span, subreddit=subreddit, interval=freqhours * 3600))
    poc(f"out of create_task {out}")
    poc("Created loop")


@bot.command(name='stopRepeat', help='Stops the loop that sends the the top reddit post.')
async def stop_post_repeat(ctx):
    """
    Function stops the loop that sends the a post in a given time interval.

    :param ctx: context of the command to which the bot is responding
    :return:
    """
    global running
    poc('Stopping Loop...')
    running = False


bot.run(TOKEN)
