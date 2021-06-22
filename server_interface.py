from mongo_api import MongoAPI
from secret import col_servers
from bson.objectid import ObjectId


def delete_guild(connection: MongoAPI, guild_id):
    if connection.delete_one(col_servers, {"guild_id": guild_id}) < 1:
        raise ConnectionError("Couldn't delete server")


class ServerInterface:
    connection: MongoAPI

    __data_dict: dict = {}

    def __init__(self, connection: MongoAPI, _guild_id: int, guild_name: str = ""):
        self.connection = connection

        self.__data_dict["guild_id"] = _guild_id
        self.__data_dict["guild_name"] = guild_name

        temp: dict = self.connection.find_one(col_servers, {"guild_id": _guild_id})

        data_dict = {"prefix": "$",
                     "guild_id": _guild_id,
                     "guild_name": guild_name,
                     "max_intervals": 50,
                     "latest_posts": [],
                     "url_backlog_size": 50,
                     "interval_ids": [],
                     "nsfw": False
                     }

        if temp is not None:
            # Check for new keys. +1 Offset for _id
            if len(temp) != len(data_dict) + 1:
                for key in data_dict.keys():
                    if key != "_id":
                        if key not in temp:
                            value = data_dict[key]
                            temp[key] = value
                            self.connection.update_one(col_servers, {"_id": temp["_id"]},
                                                       {"$set": {key: value}})

            self.__data_dict = temp
        else:
            ret = self.connection.insert_one(col_servers, data_dict)
            if type(ret) is ObjectId:
                self.__data_dict["_id"] = ret
                self.__data_dict = data_dict
            else:
                raise ConnectionError("Couldn't insert new server")

    @property
    def mongo_id(self):
        return self.__data_dict["_id"]

    @property
    def prefix(self):
        return self.__data_dict["prefix"]

    @prefix.setter
    def prefix(self, value: str):
        if type(value) is not str:
            raise TypeError("Prefix was not a string.")

        self.__data_dict["prefix"] = value
        if self.connection.update_one(col_servers, {"_id": self.__data_dict["_id"]}, {"$set": {"prefix": value}}) < 1:
            raise ConnectionError("Failed to update server")

    @property
    def nsfw(self):
        return self.__data_dict["nsfw"]

    @nsfw.setter
    def nsfw(self, value: bool):
        if type(value) is not bool:
            raise TypeError("NSFW was not a bool.")

        self.__data_dict["nsfw"] = value
        if self.connection.update_one(col_servers, {"_id": self.__data_dict["_id"]}, {"$set": {"nsfw": value}}) < 1:
            raise ConnectionError("Failed to update server")

    @property
    def guild_name(self):
        return self.__data_dict["guild_name"]

    @property
    def max_intervals(self):
        return self.__data_dict["max_intervals"]

    @property
    def latest_posts(self):
        return self.__data_dict["latest_posts"]

    @property
    def url_backlog_size(self):
        return self.__data_dict["url_backlog_size"]

    @property
    def interval_ids(self):
        return self.__data_dict["interval_ids"]

    @interval_ids.setter
    def interval_ids(self, value: list):
        self.__data_dict["interval_ids"] = value
        if self.connection.update_one(col_servers, {"_id": self.__data_dict["_id"]},
                                      {"$set": {"interval_ids": value}}) < 1:
            raise ConnectionError("Failed to update queue")

    def add_post(self, url):
        posts: list = self.__data_dict["latest_posts"]

        if url not in posts:
            self.__data_dict["latest_posts"].append(url)
            self._check_size()
            if self.connection.update_one(col_servers, {"_id": self.__data_dict["_id"]},
                                          {"$set": {"latest_posts": self.__data_dict["latest_posts"]}}) < 1:
                raise ConnectionError("Failed to update queue")

            return True

        return False

    def add_id(self):
        # checking if interval can be added
        if len(self.interval_ids) + 1 >= self.max_intervals:
            return -1

        new_id = -1

        # checking for free smaller numbers
        for i in range(len(self.interval_ids) + 1):
            if i not in self.interval_ids:
                new_id = i
                break

        if new_id < 0:
            return -1

        temp: list = self.interval_ids
        temp.append(new_id)
        temp.sort()
        self.interval_ids = temp

        return new_id

    # ==================================================================================================================
    # UTILS - these functions do not push the modifications to mongodb!!!
    # ==================================================================================================================

    def _check_size(self):
        posts: list = self.__data_dict["latest_posts"]

        if len(posts) > self.url_backlog_size:
            diff = len(posts) - self.url_backlog_size
            posts = posts[diff:]
            self.__data_dict["latest_posts"] = posts
