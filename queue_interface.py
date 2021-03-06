import datetime

from mongo_api import MongoAPI
from secret import col_queue
from bson.objectid import ObjectId


# list intervals of one server
# list all intervals
# delete interval
# add interval
# time_shift interval
# search for newest


def list_intervals(connection: MongoAPI, guild_id: int):
    intervals = connection.find(col_queue, {"guild_id": guild_id})
    return intervals


def list_all_intervals(connection: MongoAPI):
    intervals = connection.find(col_queue)
    return intervals


def delete_intervals(connection: MongoAPI, guild_id: int, interval_id: str = "*"):
    status = 0

    if interval_id == "*":
        status = connection.delete(col_queue, filter_dict={"guild_id": guild_id})
    else:
        status = connection.delete_one(col_queue, filter_dict={"guild_id": guild_id, "interval_id": int(interval_id)})

    if status < 1:
        raise ConnectionError("Failed to delete from queue")


def add_intervals(connection: MongoAPI, guild_id: int, channel: int, interval_id: int, subreddit: str, top_of: int,
                  _time_shift: float, next_post_obj: datetime.datetime):
    data_dict = {
        "guild_id": guild_id,
        "channel": channel,
        "interval_id": interval_id,
        "subreddit": subreddit,
        "top_of": top_of,
        "time_shift": _time_shift,
        "next_post_str": next_post_obj.strftime("%Y.%m.%d_%H:%M"),
        "next_post_obj": next_post_obj
    }

    ret = connection.insert_one(col_queue, data_dict)

    if type(ret) is not ObjectId:
        raise ConnectionError("Failed to insert into queue")


def time_shift(connection: MongoAPI, queue_entry_mongo_id: ObjectId, new_time_obj: datetime.datetime):
    new_time_str = new_time_obj.strftime("%Y.%m.%d_%H:%M")

    if connection.update_one(col_queue, filter_dict={"_id": queue_entry_mongo_id},
                             update_dict={"$set": {"next_post_obj": new_time_obj, "next_post_str": new_time_str}}) < 1:
        raise ConnectionError("Failed to update queue")


def next_interval(connection: MongoAPI):
    return connection.find_one(col_queue, filter_dict=None, projection_dict=None, sort=[("next_post_obj", 1)])


def queue_size(connection: MongoAPI):
    return connection.count(col_queue)
