import abc
from collections import namedtuple, AsyncIterator
from contextlib import asynccontextmanager
from typing import Dict

import aiohttp
import datetime


async def retrieve_bearer_token(api_key, api_secret_key) -> str:
    auth = aiohttp.BasicAuth(api_key, api_secret_key)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.twitter.com/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=auth,
        ) as r:
            if r.status == 403:
                raise Exception("Invaild client credentials")
            elif r.status != 200:
                raise Exception("Unknown bearer token retrieval error")

            json_response = await r.json()
            return json_response["access_token"]


class Query:
    def __init__(
        self,
        query_string: str,
        max_results: int = 250,
        from_date: datetime.datetime or None = None,
        to_date: datetime.datetime or None = None,
    ):
        self._query_string = query_string
        self._max_results = max_results
        self._to_date = to_date or datetime.datetime.utcnow()
        self._from_date = from_date or self._to_date - datetime.timedelta(days=30)

    @staticmethod
    def _datetime_to_twitter_format(datetime: datetime.datetime) -> str:
        # format: YYYYMMDDHHMM
        return datetime.strftime("%Y%m%d%H%m")

    def to_query_dict(self) -> Dict:
        return {
            "query": self._query_string,
            "maxResults": self._max_results,
            "fromDate": self._datetime_to_twitter_format(self._from_date),
            "toDate": self._datetime_to_twitter_format(self._to_date),
        }

    @property
    def results(self) -> int:
        return self._max_results


TWEETS_PER_REQUEST = 100


Credentials = namedtuple("Credentials", ("api_key", "secret_key", "app_name"))


@abc.ABC
class TweetSource:
    @abc.abstractmethod
    async def count(self, query: Query) -> int:
        pass

    @abc.abstractmethod
    async def query(self, query: Query) -> AsyncIterator[dict]:
        pass


class Client(TweetSource):
    def __init__(self, bearer_token: str, app_name: str):
        self._bearer_token = bearer_token
        self.app_name = app_name

    @classmethod
    async def from_api_key(cls, credentials: Credentials) -> 'Client':
        bearer_token = await retrieve_bearer_token(
            credentials.api_key, credentials.secret_key
        )
        return cls(bearer_token, credentials.app_name)

    @property
    def _auth_headers(self):
        return {"Authorization": f"Bearer {self._bearer_token}"}

    @asynccontextmanager
    async def _twitter_api_request(self, url, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=self._auth_headers, **kwargs
            ) as result:
                yield result

    async def query(self, query: Query) -> AsyncIterator[dict]:
        query_dict = query.to_query_dict()
        query_dict["maxResults"] = TWEETS_PER_REQUEST

        remaining_results = query.results

        while remaining_results > 0:
            async with self._twitter_api_request(
                f"https://api.twitter.com/1.1/tweets/search/30day/{self.app_name}.json",
                json=query_dict,
            ) as r:
                json_response = await r.json()
                if r.status != 200:
                    raise Exception("Tweet retrieval error")

                for tweet in json_response["results"]:
                    yield tweet

                remaining_results -= TWEETS_PER_REQUEST
                query_dict["next"] = json_response["next"]

    async def count(self, query: Query) -> int:
        query_dict = query.to_query_dict()
        del query_dict["maxResults"]

        async with self._twitter_api_request(
            f"https://api.twitter.com/1.1/tweets/search/30day/{self.app_name}/counts.json",
            json=query_dict,
        ) as r:
            json_response = await r.json()
            if r.status != 200:
                raise Exception("Tweet retrieval error")

            return json_response["totalCount"]

