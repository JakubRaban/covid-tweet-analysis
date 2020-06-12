from typing import List

from data_source import TweetSource


class UserSummary:
    def __init__(self, tweet_source: TweetSource, username: str):
        self._tweet_source = tweet_source
        self._username = username
        self.collections = [self._get_collection()]
        self._tweets = self._get_user_tweets()

    def get_results(self) -> dict:
        return {
            "Grupa społeczna": self.collections[0],
            "Tweety o koronawirusie": self._get_tweets_count(),
            "Retweety o koronawirusie": self._get_retweets_count(),
            "Własne tweety": self._get_own_tweets_count(),
            "Średnia ilość polubień": "{:.2f}".format(self._get_average_likes()),
            "Średnia ilość retweetów": "{:.2f}".format(self._get_average_retweets()),
            "Najwięcej polubień": self._get_max_likes(),
            "Najwięcej retweetów": self._get_max_retweets(),
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
        return len(self._tweets)

    def _get_retweets_count(self) -> int:
        return len(self._tweets[self._tweets['is_retweet'] == True])

    def _get_own_tweets_count(self) -> int:
        return len(self._tweets[self._tweets['is_retweet'] == False])

    def _get_average_likes(self) -> int:
        return self._tweets["favorite_count"].mean()

    def _get_average_retweets(self) -> int:
        return self._tweets["retweet_count"].mean()

    def _get_max_likes(self) -> int:
        return self._tweets["favorite_count"].max()

    def _get_max_retweets(self) -> int:
        return self._tweets["retweet_count"].max()
