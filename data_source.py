from itertools import chain
from typing import List, Iterable, Optional, Tuple

import pandas as pd
from pymongo.database import Database


class Tweets:
    def __init__(self, data_iterator: Iterable[dict]):
        self._data_iterator = data_iterator

    def to_data_frame(self):
        filtered_iterator = (
            process_tweet(x) for x in self._data_iterator if not is_faulty(x)
        )
        series = {'text': [], 'text2': []}
        for tweet in filtered_iterator:
            for key, value in tweet.items():
                series[key].append(value)
        return pd.DataFrame(series)


class TweetSource:
    def __init__(self, db: Database):
        self._db: Database = db

    @property
    def collection_names(self) -> Iterable[str]:
        return sorted(self._db.list_collection_names())

    def get_tweets(self, collections: Iterable[str], filter_params: Optional[dict] = None) -> Tweets:
        filter_params = filter_params or {}
        data_chain = chain(
            *(self._db[collection].find(filter_params) for collection in collections)
        )
        return Tweets(data_chain)


def process_tweet(tweet: dict) -> dict:
    return {
        'text': tweet.get('text', ''),
        'text2': 'twój stary'
    }


def is_faulty(tweet: dict) -> bool:
    return 'fault' in tweet
