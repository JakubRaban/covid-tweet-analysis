from typing import List

from data_source import TweetSource


class UserSummary:
    def __init__(self, tweet_source: TweetSource, username: str):
        self._tweet_source = tweet_source
        self._username = username
        self.collections = [self._get_collection()]

    def get_results(self) -> dict:
        return {
            "Grupa społeczna": self.collections[0],
            "Tweety o koronawirusie": self._get_tweets_count(),
            "Retweety o koronawirusie": self._get_tweets_count(),
        }

    def _get_collection(self) -> str:
        social_groups = self._tweet_source.collection_names
        for possible_social_group in social_groups:
            if self._tweet_source.get_tweets([possible_social_group], {"user.name": self._username}):
                return possible_social_group

    def _get_user_tweets(self):
        return self._tweet_source.get_tweets(
            self.collections,
            {"user.name": self._username}
        ).to_data_frame()

    def _get_tweets_count(self) -> int:
        return len(self._get_user_tweets())

    def _get_retweeted_tweets_count(self, collections: List[str]) -> int:
        tweets = self._get_user_tweets()
        return len(tweets[tweets['retweet_count'] > 0])