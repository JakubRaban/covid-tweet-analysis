import abc
import datetime
from collections import AsyncIterator, namedtuple
from contextlib import asynccontextmanager
from typing import Dict

import aiohttp


async def retrieve_bearer_token(api_key, api_secret_key) -> str:
    auth = aiohttp.BasicAuth(api_key, api_secret_key)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.twitter.com/oauth2/token", data={"grant_type": "client_credentials"}, auth=auth,
        ) as r:
            if r.status == 403:
                raise Exception("Invaild client credentials")
            elif r.status != 200:
                raise Exception("Unknown bearer token retrieval error")

            json_response = await r.json()
            return json_response["access_token"]


TWEETS_PER_REQUEST = 100

class APIQuery(abc.ABC):

    @abc.abstractmethod
    def to_query_dict(self) -> Dict:
        ...

    @abc.abstractstaticmethod
    def _datetime_to_twitter_format(datetime: datetime.datetime) -> str:
        ...


class PremiumQuery(APIQuery):
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


class StandardQuery(APIQuery):
    def __init__(
        self,
        query_string: str,
        max_results: int = 250,
        lang: str or None = None,
        until: datetime.datetime or None = None,
        tweet_mode: str = 'extended'
    ):
        self._query_string = query_string
        self._max_results = max_results
        self._lang = lang
        self._until = until or datetime.datetime.now()
        self._tweet_mode = tweet_mode

    @staticmethod
    def _datetime_to_twitter_format(datetime: datetime.datetime) -> str:
        return datetime.strftime("%Y-%m-%d")

    def to_query_dict(self) -> Dict:
        return {
            "q": self._query_string,
            "count": TWEETS_PER_REQUEST,
            "until": self._datetime_to_twitter_format(self._until),
            'tweet_mode': self._tweet_mode,
            'lang': self._lang or ''
        }

    @property
    def results(self) -> int:
        return self._max_results


Credentials = namedtuple("Credentials", ("api_key", "secret_key", "dev_env"))


class Client(abc.ABC):
    def __init__(self, bearer_token: str, dev_env: str):
        self._bearer_token = bearer_token
        self.dev_env = dev_env

    @classmethod
    async def from_api_key(cls, credentials: Credentials) -> "Client":
        bearer_token = await retrieve_bearer_token(credentials.api_key, credentials.secret_key)
        return cls(bearer_token, credentials.dev_env)

    @property
    def _auth_headers(self):
        return {"Authorization": f"Bearer {self._bearer_token}"}

    @abc.abstractmethod
    async def query(self, query: APIQuery):
        pass


class PremiumClient(Client):
    def __init__(self, *args, product, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.product = product

    @asynccontextmanager
    async def _twitter_api_request(self, url, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self._auth_headers, **kwargs) as result:
                yield result

    async def query(self, query: PremiumQuery) -> AsyncIterator:
        query_dict = query.to_query_dict()
        query_dict["maxResults"] = TWEETS_PER_REQUEST

        remaining_results = query.results

        while remaining_results > 0:
            async with self._twitter_api_request(
                f"https://api.twitter.com/1.1/tweets/search/{self.product}/{self.dev_env}.json",
                json=query_dict
            ) as r:
                json_response = await r.json()
                if r.status != 200:
                    raise Exception(f"Tweet retrieval error, status: {r.status}, {await r.text()}")

                for tweet in json_response["results"]:
                    yield tweet

                remaining_results -= TWEETS_PER_REQUEST
                if "next" in json_response:
                    query_dict["next"] = json_response["next"]
                else:
                    break

    async def count(self, query: PremiumQuery) -> int:
        query_dict = query.to_query_dict()
        del query_dict["maxResults"]

        async with self._twitter_api_request(
            f"https://api.twitter.com/1.1/tweets/search/30day/{self.app_name}/counts.json", json=query_dict,
        ) as r:
            json_response = await r.json()
            if r.status != 200:
                raise Exception("Tweet retrieval error")

            return json_response["totalCount"]


class StandardClient(Client):
    @asynccontextmanager
    async def _twitter_api_request(self, url, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._auth_headers, **kwargs) as result:
                yield result

    async def query(self, query: StandardQuery) -> AsyncIterator:
        query_dict = query.to_query_dict()

        remaining_results = query.results

        while remaining_results > 0:
            async with self._twitter_api_request(
                f"https://api.twitter.com/1.1/search/tweets.json",
                params=query_dict
            ) as r:
                json_response = await r.json()
                if r.status != 200:
                    raise Exception(f"Tweet retrieval error, status: {r.status}, {await r.text()}")

                for tweet in json_response["statuses"]:
                    yield tweet

                remaining_results -= TWEETS_PER_REQUEST
                if "next" in json_response:
                    query_dict["next"] = json_response["next"]
                else:
                    break


class FakeClient(PremiumClient):
    def __init__(self) -> None:
        pass

    async def count(self, query: APIQuery) -> int:
        return 1

    async def query(self, query: APIQuery) -> AsyncIterator:
        yield {"__test": True, "id": 2137}
        yield {"__test": True, "id": 1488}
        yield {"__test": True, "id": 420}
