from collections import Iterable
from contextlib import contextmanager

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient


def mongo_storage(connection_url: str, database_name: str):
    return


class DatabaseConnection:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    @classmethod
    def connect(cls, connection_url: str, database_name: str):
        connection = AsyncIOMotorClient(connection_url)
        database = connection[database_name]
        return cls(database)

    async def insert(self, tweet: dict, collection: str):
        await self._db[collection].insert_one(tweet)

    async def bulk_insert(self, tweets: Iterable, collection: str):
        await self._db[collection].insert_many(tweets)
