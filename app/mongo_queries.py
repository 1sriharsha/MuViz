import pymongo


class MongoOperations:
    def __init__(self, uri, limit=200):
        self.__uri = uri
        self.limit = limit
        self.connected = False

    def check_connected(self, func):
        def inner():
            try:
                self.connected = self.mongo_connection.get_database(self.db_name)
                if self.connected:
                    func()
                    return True
                else:
                    return False
            except Exception as e:
                return e

        return inner()

    def connect(self, database, collection_name):
        try:
            self.mongo_connection = pymongo.MongoClient(self.__uri)
            self.db_name = database
            self.collection_name = collection_name
            self.db = self.mongo_connection[self.db_name]
            if self.mongo_connection.get_database(database) is not None:
                return True
            else:
                return False
        except Exception as e:
            print("ERROR- Cannot connect to db", e)
            return False

    # @check_connected
    def search_song_by_name(self, song_name):
        songs = []
        try:
            for i in self.db[self.collection_name].find({"name": song_name}, {"_id": 0}):
                songs.append(i)
        except Exception as e:
            print("error in ", self.__class__, " ", e)
        return songs

    def search_song_by_regex(self, song_name):
        try:
            query = [
                {
                    '$match': {
                        'name': {
                            '$regex': '^.*' + song_name + '.*$',
                            '$options': 'i'
                        }
                    }
                }, {'$limit': 50}, {
                    '$project': {
                        'name': 1,
                        'len': {
                            '$strLenCP': '$name'
                        }
                    }
                }, {
                    '$sort': {
                        'len': 1
                    }
                }, {
                    '$unset': '_id'
                }, {
                    '$unset': 'len'
                }, {"$group": {"_id": None,
                               "name": {"$addToSet": "$name"}
                               }},
                {
                    '$unset': '_id'
                }
            ]
            return list(self.db[self.collection_name].aggregate(query,
                                                                cursor={},
                                                                allowDiskUse=True))
        except Exception as e:
            print("error in ", self.__class__, " ", e)
        return []

    def stats(self):
        res = []
        try:
            for i in self.db[self.collection_name].find({}):
                res.append(i)
        except Exception as e:
            print("error in ", self.__class__, " ", e)
        return res

    def exec_query(self, attribute, comparision, value):
        songs = []
        try:
            for i in list(self.db[self.collection_name].aggregate([{"$match":
                                                                        {attribute:
                                                                             {comparision: value}}
                                                                    },
                                                                   {'$limit': self.limit},
                                                                   {"$unset": ["_id","acousticness","album_id", "danceability", "disc_number", "energy", "explicit", "instrumentalness", "key", "liveness", "loudness", "mode", "speechiness", "tempo", "time_signature", "track_number", "valence", "year"]}],
                                                                  cursor={}, allowDiskUse=True)):
                songs.append(i)
        except Exception as e:
            print("error in ", self.__class__, " ", e)
        return songs
