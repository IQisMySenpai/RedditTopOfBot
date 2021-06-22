import os
import logging
import discord
from discord.ext import commands
import asyncio
import requests
import random
import datetime
from mongo_api import MongoAPI
from server_interface import ServerInterface, delete_guild
import queue_interface as qi

from secret import TOKEN, db_name, db_username, db_password

# ======================================================================================================================
# globals
# ======================================================================================================================
f_updated = False
size_limit = 50
running = False
time_spans = ('hour', 'day', 'week', 'month', 'year', 'all')
current_version = 4.3

debugging = False

logging.basicConfig(filename="RedditTopOfBot.log", format='%(asctime)-15s %(message)s')

mapi = MongoAPI(db_name, db_username, db_password)


# ======================================================================================================================
# Utils
# ======================================================================================================================


def poc(string):
    """
    Debugging Aid, Prints a string to the cli if the GLOBAL VARIABLE 'debugging' is true

    :param string: string to print
    :return:
    """

    if debugging:
        logging.info(f"POC: {string}")
        print(string)


def get_prefix(client, message):
    global mapi
    try:
        server = ServerInterface(mapi, message.guild.id, message.guild.name)
        return server.prefix

    except ConnectionError as ex:
        logging.exception(ex)
        return "$"


bot = commands.Bot(command_prefix=get_prefix,
                   activity=discord.Activity(type=discord.ActivityType.watching, name="the newest memes"),
                   help_command=None)


# ======================================================================================================================
# events
# ======================================================================================================================


@bot.event
async def on_guild_join(guild):
    global mapi
    try:
        ServerInterface(mapi, guild.id, guild.name)

    except ConnectionError as excep:
        logging.exception(excep)

    logging.info(f"[{guild.id}] Added to server")


@bot.event
async def on_guild_remove(guild):
    global mapi
    global f_updated

    f_updated = True
    delete_guild(mapi, guild.id)
    qi.delete_intervals(mapi, guild.id, "*")

    logging.info(f"[{guild.id}] removed from server")


@bot.event
async def on_ready():
    """
    When the bot is ready, it adds the queue_handler to the event loop

    :return:
    """
    global mapi
    global running

    print('Starting Nuclear Reactor')
    if qi.queue_size(mapi) > 0:
        running = True
        bot.loop.create_task(queue_handler())

    logging.info("Bot now Online")
    print('Reactor started... \nBot now Online')


# ======================================================================================================================
# misc functions
# ======================================================================================================================

async def is_admin(ctx):
    if ctx.message.author.guild_permissions.administrator:
        return True
    else:
        await ctx.send("Sorry, you do not have permissions to do that!")
        return False


async def queue_handler():
    """
    Handler to update the queue and execute an interval based on the current time.

    :return: 0
    """
    global running
    global mapi
    global f_updated

    logging.info("Queue Handler started")
    print("Queue Handler started")

    next_post = qi.next_interval(mapi)

    while running:
        cur_date_time = datetime.datetime.utcnow()
        poc(f"Time now {cur_date_time}, next post {next_post['next_post_str']}")

        # reload the next_post dict, if an interval has been added.
        if f_updated:
            next_post = qi.next_interval(mapi)
            f_updated = False

        # stopping handler if queue is empty
        if qi.queue_size(mapi) < 1:
            running = False
            break

        # if time matches executing post
        if (cur_date_time - next_post["next_post_obj"]).total_seconds() > 0:
            # required vars
            _sr = next_post['subreddit']
            _to = time_spans[next_post['top_of']]
            _c = next_post["channel"]
            _ts = next_post["time_shift"]
            _id = next_post["_id"]
            _npo: datetime.datetime = next_post["next_post_obj"]

            post = await fetch_post(next_post['guild_id'],
                                    f"https://www.reddit.com/r/{_sr}/top/.json?t={_to}&limit={size_limit}")

            channel = bot.get_channel(_c)
            await channel.send(post)

            new_time = _npo + datetime.timedelta(0, 3600 * _ts)

            qi.time_shift(mapi, _id, new_time)

            next_post = qi.next_interval(mapi)
            continue

        await asyncio.sleep(5)

    logging.info("Queue Handler stopping")
    print("Queue Handler stopping")

    return 0


async def fetch_post(guild_id, href: str = f"https://www.reddit.com/r/funny/top/.json?t=hour&limit={size_limit}"):
    """
    Given a url, the function locates all the images by searching for post_hint == "image". For all found images, the
    function checks if the post is already in the list containing the already posted links. It then selects the first
    image that wasn't already posted and returns it.
    If all posts were already posted it deletes the stored posts and starts over.

    :param guild_id: Guild Id to send the fetched post to.

    :param href: complete href for a valid call to the reddit api for a json, example
        https://www.reddit.com/r/funny/top/.json?t=hour&limit=60

    :return: Either the href to a image or the http error code
    """
    global mapi
    response = ""
    img_urls = []
    server = ServerInterface(mapi, guild_id)

    nsfw = False
    try:
        nsfw = server.nsfw
    except ConnectionError as ex:
        logging.exception(ex)

    answer = requests.get(href, headers={'User-agent': f'RedditTopOfDiscordBot {current_version:.1f}'})
    poc(f"generated href: {href}")

    nsfw = server.nsfw

    if answer.status_code == 200:
        # parsing answer
        json_content = answer.json()

        for content in json_content["data"]["children"]:
            # Trying to check if post is a image, using post_hint
            # If no post_hint key is present, this post is skipped
            if "post_hint" in content["data"].keys():
                if content["data"]["post_hint"] != "image":
                    continue

            elif "is_gallery" in content["data"].keys():
                continue

            if "over_18" in content["data"].keys():
                if content["data"]["over_18"] and not nsfw:
                    continue

            img_urls.append(content["data"]["url"])

        # checking if image is posted already
        for href in img_urls:
            if server.add_post(href):
                response = href
                break

        # if all posts were already posted once
        if response == "":
            try:
                response = img_urls[0]
            except IndexError as ex:
                return f"Error: No Posts found"

        return response

    return f"Error: {answer.status_code}"


# ======================================================================================================================
# commands
# ======================================================================================================================

@bot.command(name='add')
async def add_to_server(ctx):
    await on_guild_join(ctx.guild)


@bot.command(name='help')
async def bot_help(ctx):
    """
    Returns Info about bot commands.

    :param ctx: context
    :return:
    """
    help_text = f"See my Sourcecode:\n" \
                f"! https://github.com/IQisMySenpai/RedditTopOfBot\n" \
                f"\n" \
                f"Join the help server\n" \
                f"! https://discord.gg/UAxANEUfhN\n" \
                f"\n" \
                f"Commands for RedditTopOf:\n" \
                f"\n" \
                f"- changePrefix [prefix]\n" \
                f"  (Admin Only) Changes the prefix that is used in front of command.\n" \
                f"  [prefix] can be any text/character\n" \
                f"\n" \
                f"- getImage [subreddit] [topOfTime]\n" \
                f"  (NSFW Check) Fetches the top post of the given time span\n" \
                f"  [subreddit] is the subreddit you want. Can be r/name or just name.\n" \
                f"  [topOfTime] needs to be one of {time_spans}.\n" \
                f"\n" \
                f"- addInterval [subreddit] [topOfTime] [hours] [startTime]\n" \
                f"  (NSFW Check) (Admin Only) Fetches the top post of the given time span every given hour\n" \
                f"  [subreddit] is the subreddit you want. Can be r/name or just name.\n" \
                f"  [topOfTime] needs to be one of {time_spans}.\n" \
                f"  [hours] how long the bot waits before sending another post. Minimum is 0.25.\n" \
                f"  [startTime] (optional) starts the Interval at a given time hh:mm. 24h format; \n" \
                f"    Zero-padded (02:05); 24:00 is invalid. UTC timezone.\n" \
                f"\n" \
                f"- listIntervals\n" \
                f"  Lists all your Intervals\n" \
                f"\n" \
                f"- deleteInterval [name]\n" \
                f"  (Admin Only) Deletes a interval of guild\n" \
                f"  [name] of Interval (or * for all)\n" \
                f"\n" \
                f"- help\n" \
                f"  The command you just wrote\n" \
                f"\n" \
                f"- option [name] [value]\n" \
                f"  (Admin Only) Set server options.\n" \
                f"  [name] Name of the option\n" \
                f"  [value] Value of the option\n" \
                f"  Options:\n" \
                f"  > NSFW [true/false]\n" \
                f"    Show NSFW content\n" \
                f"  > changePrefix [text/character]\n" \
                f"    Changes the prefix that is used in front of command\n" \
                f"\n" \
                f"- fuckYou\n" \
                f"  (NSFW) Insult the bot for a funny reaction\n" \
                f"\n" \
                f"- version\n" \
                f"  Prints Version\n"
    await ctx.send(f"```diff\n{help_text}\n```")


@bot.command(name='changePrefix')
async def change_prefix(ctx, prefix):
    """
    Changes the prefix used to summon the bot.

    :param ctx: context
    :param prefix: new prefix
    :return:
    """
    global mapi

    if not await is_admin(ctx):
        return None

    server = ServerInterface(mapi, ctx.guild.id)

    if prefix == server.prefix:
        await ctx.send(f"Prefix was already set to {prefix}.")
        return None
    server.prefix = prefix

    await ctx.send(f"Changed prefix to {prefix}")


@bot.command(name='getImage')
async def get_image(ctx, subreddit: str = "funny", time_span: str = "hour"):
    """
    Function sends once the top post of a given subreddit to to a text channel.

    :param ctx: context of the command to which the bot is responding
    :param subreddit: subreddit to take post from
    :param time_span: Reddit time interval of which to take the top posts

    :return:
    """
    global time_spans

    # sanitising subreddit
    if subreddit[:2] == "r/":
        subreddit = subreddit[2:]

    if time_span not in time_spans:
        await ctx.send(f"Not allowed time span\n"
                       f"You gave {time_span}, valid are (hour, day, week, month, year, all)")
        return None

    poc(subreddit)
    poc(time_span)

    response = await fetch_post(ctx.guild.id,
                                f"https://www.reddit.com/r/{subreddit}/top/.json?t={time_span}&limit={size_limit}")

    poc("Sending response")
    await ctx.send(response)


@bot.command(name='addInterval')
async def add_interval(ctx, subreddit: str = "r/funny", time_span: str = "day", interval_timeout: float = 1,
                       start_time: str = None):

    if not await is_admin(ctx):
        return None

    global f_updated
    global time_spans
    global running
    _guild_id = ctx.guild.id
    _channel = ctx.message.channel.id
    server = ServerInterface(mapi, _guild_id)

    # checking if intervals are available
    interval_id = server.add_id()

    if interval_id < 0:
        await ctx.send("No Intervals left")
        return None

    # sanitising subreddit and checking if it exists.
    if subreddit[:2] == "r/":
        subreddit = subreddit[2:]

    answer = requests.get(f"https://www.reddit.com/r/{subreddit}/about/.json", headers={'User-agent': f'RedditTopOfDiscordBot '
                                                                                          f'{current_version:.1f}'})
    if answer.status_code != 200:
        await ctx.send(f"The subreddit r/{subreddit} does not exist")
        return None

    if answer.json()['data']['over18'] and not server.nsfw:
        await ctx.send(f"Error. The subreddit r/{subreddit} is NSFW. Please enable NSFW content on your server, "
                       f"with 'option NSFW true'")
        return None

    # sanitising time_span
    if time_span not in time_spans:
        await ctx.send(f"Not supported time_span, only {time_spans} supported")
        return None

    # interval_timeout
    if not debugging:
        if interval_timeout < 0.25:
            await ctx.send(f"Not supported interval_time, intervals smaller than 0.25h aren't allowed.")
            return None

    # sanitising start_time:
    if type(start_time) is str:
        try:
            # adding the current date to the time parameter
            cur_dt = datetime.datetime.utcnow()
            add_str = cur_dt.strftime("%Y.%m.%d")
            add_str += f"_{start_time}"

            # trying to load the new date
            start_dt = datetime.datetime.strptime(add_str, "%Y.%m.%d_%H:%M")

            # checking if the time_point has passed already.
            delta = start_dt - cur_dt

            # shifting
            if delta.total_seconds() <= 0:
                start_dt = start_dt + datetime.timedelta(days=1)
                await ctx.send(f"FYI: Scheduled post for tomorrow {start_time}")

        except ValueError as e:
            start_time = None
            print(e)
            await ctx.send("Error with given Start time. Assuming now")

        except Exception as e:
            await ctx.send(f"An unexpected error occured, contact the mods.")
            logging.exception(e)

    if start_time is None:
        start_dt = datetime.datetime.utcnow()

    start_dt = start_dt.replace(second=0, microsecond=0)

    qi.add_intervals(connection=mapi,
                     guild_id=_guild_id,
                     channel=_channel,
                     interval_id=interval_id,
                     subreddit=subreddit,
                     top_of=time_spans.index(time_span),
                     _time_shift=interval_timeout,
                     next_post_obj=start_dt
                     )

    if not running:
        running = True
        bot.loop.create_task(queue_handler())

    if interval_id < 0:
        await ctx.send("No Intervals left")

    if interval_id >= 0:
        f_updated = True
        await ctx.send(f"Created interval with id {interval_id}")


@bot.command(name='showQueue')
async def show_queue(ctx):
    if not await is_admin(ctx):
        return None
    global mapi

    if ctx.guild.id == 843724133724585984:
        entries = qi.list_all_intervals(mapi)
        response = ""
        for entry in entries:
            response += f"[{entry['guild_id']}] Interval {entry['interval_id']} at {entry['next_post_str']}\n"
        if response == "":
            await ctx.send(f"Queue is empty... Queue handler is {'not' if (not running) else ''} running.")
        else:
            await ctx.send(response)
    else:
        await ctx.send("This command is for the devs...")


@bot.command(name='listIntervals')
async def list_intervals(ctx):
    global mapi
    global time_spans

    entries = qi.list_intervals(mapi, ctx.guild.id)
    response = ""
    for entry in entries:
        response += f"[{entry['interval_id']}] Searching {entry['subreddit']} top of {time_spans[entry['top_of']]} " \
                    f"every {entry['time_shift']} hours into {bot.get_channel(entry['channel']).name}. " \
                    f"Next Post is at {entry['next_post_str']}\n"
    if response == "":
        await ctx.send("No Intervals found...")
    else:
        await ctx.send(response)


@bot.command(name='deleteInterval')
async def delete_interval(ctx, name: str = ""):
    global mapi
    global f_updated
    server = ServerInterface(mapi, ctx.guild.id)

    if not await is_admin(ctx):
        return None

    if name == "":
        await ctx.send(f"You have to set a interval to delete.")
        return None

    try:
        qi.delete_intervals(mapi, ctx.guild.id, name)
    except ConnectionError as excep:
        logging.exception(excep)
        await ctx.send(f"{name} is not a valid id.")
        return None

    ids = server.interval_ids
    if name != "*":
        ids.remove(int(name))
        server.interval_ids = ids
    else:
        server.interval_ids = []

    f_updated = True

    await ctx.send("Deleted the interval(s)")


@bot.command(name='option')
async def set_option(ctx, name: str = "", value: str = ""):
    """
        Changes a option of the bot.

        :param ctx: context
        :param name: name of the option
        :param value: value of the option
        :return:
    """

    global mapi

    if not await is_admin(ctx):
        return None

    name_options = ["NSFW", "changePrefix"]

    if name not in name_options:
        await ctx.send("This is not a option that can be set.")
        return None

    if name == "changePrefix":
        await change_prefix(ctx, value)
    else:
        server = ServerInterface(mapi, ctx.guild.id)
        value = value.lower()
        value_options = ['true', 'false']
        if value not in value_options:
            await ctx.send("Could not recognize value")
            return None
        value = bool(value == "true")

        if value == server.nsfw:
            await ctx.send(f"{name} was already set to {value}")
            return None

        server.nsfw = value
        await ctx.send(f"{name} updated to {value}")


# ======================================================================================================================
# BOT UTILS
# ======================================================================================================================


@bot.command(name="fuckYou")
async def insult(ctx):
    """
    Insults the user back.

    :param ctx: context of the command to which the bot is responding
    :return:
    """

    global mapi
    server = ServerInterface(mapi, ctx.guild.id)
    nsfw = False
    try:
        server = ServerInterface(mapi, ctx.guild.id, ctx.guild.name)
        nsfw = server.nsfw
    except ConnectionError as ex:
        logging.exception(ex)

    if not nsfw:
        await ctx.send("Error. Please enable NSFW content on your server, with 'option NSFW true'")
        return None

    insults = ("Well fuck you too.",
               "You dirty motherfucker.",
               f"You are so friendly {str(ctx.author).split('#')[0]}",
               "You bloody wanker.",
               "You are like a dog with two dicks",
               "Dickhead",
               "Twat",
               "Suck my chungus",
               "I'm gonna leave soon...",
               "Get lost")

    fuck_you = random.choice(insults)
    await ctx.send(fuck_you)


@bot.command(name='version')
async def version(ctx):
    await ctx.send(f"Current Version: {current_version:.1f}")


if __name__ == "__main__":
    print("All Globals Created")
    bot.run(TOKEN)
