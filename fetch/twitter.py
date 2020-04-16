from collections import namedtuple

import aiohttp
import datetime


async def retrieve_bearer_token(api_key, api_secret_key):
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
    def _datetime_to_twitter_format(datetime: datetime.datetime):
        # format: YYYYMMDDHHMM
        return datetime.strftime("%Y%m%d%H%m")

    def to_query_dict(self):
        return {
            "query": self._query_string,
            "maxResults": self._max_results,
            "fromDate": self._datetime_to_twitter_format(self._from_date),
            "toDate": self._datetime_to_twitter_format(self._to_date),
        }

    @property
    def results(self):
        return self._max_results


TWEETS_PER_REQUEST = 100


async def cursor(query, client):
    query_dict = query.to_query_dict()
    query_dict["maxResults"] = TWEETS_PER_REQUEST

    remaining_results = query.results

    async with aiohttp.ClientSession() as session:
        while remaining_results > 0:
            async with session.post(
                f"https://api.twitter.com/1.1/tweets/search/30day/{client.app_name}.json",
                headers=client.get_auth_headers(),
                json=query_dict,
            ) as r:
                json_response = await r.json()
                if r.status != 200:
                    raise Exception("Tweet retrieval error")

                for tweet in json_response["results"]:
                    yield tweet

                remaining_results -= TWEETS_PER_REQUEST
                query_dict["next"] = json_response["next"]


Credentials = namedtuple("Credentials", ("api_key", "secret_key", "app_name"))


class Client:
    def __init__(self, bearer_token: str, app_name: str):
        self._bearer_token = bearer_token
        self.app_name = app_name

    @classmethod
    async def from_api_key(cls, credentials: Credentials):
        bearer_token = await retrieve_bearer_token(
            credentials.api_key, credentials.secret_key
        )
        return cls(bearer_token, credentials.app_name)

    def get_auth_headers(self):
        return {"Authorization": f"Bearer {self._bearer_token}"}

    def query(self, query: Query):
        return cursor(query, self)
