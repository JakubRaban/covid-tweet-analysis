from itertools import chain
from typing import Collection, Iterable, Optional, NamedTuple

import pandas as pd
from pymongo.database import Database


class Tweets:
    def __init__(self, data_iterator: Iterable[dict]):
        self._data_iterator = data_iterator

    def to_data_frame(self):
        filtered_iterator = (
            process_tweet(x) for x in self._data_iterator if not is_faulty(x)
        )
        series = {key: [] for key in TWEET_FIELDS.keys()}
        for tweet in filtered_iterator:
            for key, value in tweet.items():
                series[key].append(value)
        return pd.DataFrame({
            name: pd.Series(values, dtype=TWEET_FIELDS[name][0]) for name, values in series.items()
        })


UserGroup = NamedTuple('UserGroup', (('name', str), ('users', Iterable[str]), ('description', str)))


class TweetSource:
    def __init__(self, db: Database):
        self._db: Database = db

    @property
    def collection_names(self) -> Iterable[str]:
        return sorted(self._db.list_collection_names())

    def get_user_groups(self):
        # TODO temporary solution
        for group_name in self.collection_names:
            if group_name == 'test1':
                continue
            description = "Brak opisu"
            usernames = list(set(tweet['user']['name'] for tweet in self._db[group_name].find()))
            yield UserGroup(group_name, usernames, description)

    def get_tweets(self, collections: Iterable[str], filter_params: Optional[dict] = None) -> Tweets:
        filter_params = filter_params or {}
        data_chain = chain(
            *(self._db[collection].find(filter_params) for collection in collections)
        )
        return Tweets(data_chain)


TWEET_FIELDS = {
    'text': ('str', lambda tweet: tweet.get('text', '')),
}


def process_tweet(tweet: dict) -> dict:
    return {name: f(tweet) for name, (_, f) in TWEET_FIELDS.items()}


def is_faulty(tweet: dict) -> bool:
    return 'fault' in tweet
