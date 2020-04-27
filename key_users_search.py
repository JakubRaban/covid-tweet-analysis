import argparse
import json
import os
import time
from dataclasses import dataclass
from functools import reduce
from pprint import pprint
from typing import Optional

import tweepy
from pymongo import MongoClient
from pymongo.collection import Collection

not_a_retweet_query = {'retweeted_status': {"$exists": False}}


@dataclass
class Tweet:
    id: int
    retweet_count: int
    favorite_count: int
    created_at: str
    retweeted: bool

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, o: object) -> bool:
        if hasattr(o, "id"):
            return o.id == self.id
        elif isinstance(o, int):
            return o == self.id
        else:
            return False

    def to_dict(self):
        return {
            "id": self.id,
            "retweet_count": self.retweet_count,
            "favourite_count": self.favorite_count,
            "created_at": str(self.created_at),
        }


@dataclass
class User:
    id: int
    name: str
    followers_count: int
    friends_count: int
    statuses_count: int

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, o: object) -> bool:
        if hasattr(o, "id"):
            return o.id == self.id
        elif isinstance(o, int):
            return o == self.id
        else:
            return False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "followers_count": self.followers_count,
            "friends_count": self.friends_count,
            "statuses_count": self.statuses_count,
        }


def aggregate_results(tweets):
    return {
        "max_retweets": max(tweets, key=lambda tweet: tweet.retweet_count).retweet_count,
        "max_favorite": max(tweets, key=lambda tweet: tweet.favorite_count).favorite_count,
        "original_tweets": reduce(lambda acc, tweet: acc + 1 if not tweet.retweeted else acc, tweets, 0),
        "retweeted_tweets": reduce(lambda acc, tweet: acc + 1 if tweet.retweeted else acc, tweets, 0),
        "total_tweets": len(tweets),
    }


def dump_user_tweets(user_tweets: dict, path: str = None, include_tweets: bool = False):
    result = []
    total_tweets = 0

    for user, tweets in user_tweets.items():
        aggregated = aggregate_results(tweets)
        total_tweets += aggregated["total_tweets"]
        user_dict = {**user.to_dict(), "summary": aggregated}
        if include_tweets:
            user_dict["tweets"] = [tweet.to_dict() for tweet in tweets]

        result.append(user_dict)

    result = {
        "total_tweets": total_tweets,
        "total_users": len(user_tweets.keys()),
        "users_tweets": sorted(result, key=lambda user: user["summary"]["total_tweets"], reverse=True),
    }

    if path is not None:
        with open(path, "w") as f:
            json.dump(result, f, indent=2)
    else:
        pprint(result)


def dig_from_twitter(api, mongo_collection: Optional[Collection] = None,
                     query: str = '', max_tweets: int = 500, lang: str = "pl"):
    tweet_count = 0
    user_tweets = dict()
    print(query)

    cursor = tweepy.Cursor(api.search, q=query, result_type="mixed",
                           lang=lang, count=min(100, max_tweets)).items()
    try:
        while tweet_count < max_tweets:
            try:
                tweet = next(cursor)
            except tweepy.TweepError as e:
                print(
                    f"Rate limit possibly exceeded, sleeping for 15 minutes (limit time window)... {e}\n"
                    f"Current tweet count: {tweet_count}"
                )
                time.sleep((15 * 60) + 5)
                continue
            except StopIteration:
                print("No more tweets for this query :(")
                break

            if mongo_collection is not None:
                mongo_collection.insert_one(tweet._json)

            if tweet.user.id in user_tweets.keys():
                user = tweet.user.id
            else:
                user = User(
                    tweet.user.id,
                    tweet.user.screen_name,
                    tweet.user.followers_count,
                    tweet.user.friends_count,
                    tweet.user.statuses_count,
                )
                user_tweets[user] = set()

            if tweet.id not in user_tweets[user]:
                tweet = Tweet(tweet.id, tweet.retweet_count, tweet.favorite_count,
                              tweet.created_at, hasattr(tweet, 'retweeted_status'))
                user_tweets[user].add(tweet)

            tweet_count += 1

    except KeyboardInterrupt:
        print("Search was interrupted, closing up...")
    except Exception as e:
        print(f"Unexpected error during search: {e}. Closing up...")

    return user_tweets


def dig_from_mongo(mongo_collection: Collection, query: dict = {}, max_tweets: int = 500):
    user_tweets = {}
    tweet_count = 0
    for tweet in mongo_collection.find(query):
        if tweet['user']['id'] in user_tweets.keys():
            user = tweet['user']['id']
        else:
            user = User(
                tweet['user']['id'],
                tweet['user']['screen_name'],
                tweet['user']['followers_count'],
                tweet['user']['friends_count'],
                tweet['user']['statuses_count'],
            )
            user_tweets[user] = set()

        if tweet['id'] not in user_tweets[user]:
            tweet = Tweet(tweet['id'], tweet['retweet_count'], tweet['favorite_count'],
                          tweet['created_at'], 'retweeted_status' in tweet)
            user_tweets[user].add(tweet)

        tweet_count += 1
        if tweet_count == max_tweets:
            break

    return user_tweets


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Key Twitter User Search",
        description="Digs through tweets from standard search API to find the most relevant users for given query",
    )

    parser.add_argument("dig_from", type=str, choices=["twitter", "mongo"], help="place to retrieve the tweets from")
    parser.add_argument("--max-tweets", type=int, default=20, help="maximum number of tweets to be retrieved from API")
    parser.add_argument("--query", type=str, default="koronawirus", help="query used in Twitter search requests")
    parser.add_argument("--lang", type=str, default="pl", help="language of retrieved tweets (ISO 639-1 code)")
    parser.add_argument("--dump-path", type=str, default=None, help="path to dump retrieved data")
    parser.add_argument("--persist-in-mongo", type=bool, default=False,
                        help="save tweets to MongoDB when downloaded from Twitter")

    args = parser.parse_args()

    mongo = MongoClient("localhost", 27017)
    mongo_db = mongo["twitter_dump"]

    api_key, api_secret_key = os.getenv("API_KEY"), os.getenv("API_SECRET_KEY")
    access_token, access_token_secret = os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    max_tweets = args.max_tweets
    query = args.query

    if args.dig_from == "twitter":
        collection = mongo_db.covid_tweets if args.persist_in_mongo else None
        user_tweets = dig_from_twitter(api, collection, query, max_tweets, args.lang)
    else:
        user_tweets = dig_from_mongo(mongo_db.covid_tweets, query={}, max_tweets=max_tweets)

    dump_user_tweets(user_tweets, path=args.dump_path)


