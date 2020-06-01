from typing import List

from data_source import TweetSource


class UserSummary:
    def __init__(self, tweet_source: TweetSource, username: str):
        self._tweet_source = tweet_source
        self._username = username

    def get_results(self) -> dict:
        collections = [self._get_social_group()]
        return {
            "Grupa społeczna": collections[0],
            "Ilość tweetów": self._get_tweets_count(collections),
        }

    def _get_social_group(self) -> str:
        social_groups = self._tweet_source.collection_names
        for possible_social_group in social_groups:
            if self._tweet_source.get_tweets([possible_social_group], {"user.name": self._username}):
                return possible_social_group

    def _get_tweets_count(self, collections: List[str]) -> str:
        tweets = self._tweet_source.get_tweets(collections, {"user.name": self._username}).to_data_frame()
        return len(tweets)