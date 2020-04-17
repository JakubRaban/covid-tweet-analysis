import asyncio
import os
from collections import namedtuple

from fetch import twitter, database

TWITTER_API_KEY_ENVVAR = "TWITTER_API_KEY"
TWITTER_API_SECRET_ENVVAR = "TWITTER_API_SECRET"


async def fetch(
    query: twitter.Query, source: twitter.TweetSource, database
):
    client = await twitter.Client.from_api_key(twitter_credentials)

    async for tweet in client.query(query):
        database.upload_tweet(tweet)


async def main():
    api_key = os.getenv(TWITTER_API_KEY_ENVVAR)
    secret_key = os.getenv(TWITTER_API_SECRET_ENVVAR)
    if not api_key or not secret_key:
        print(
            f"You must specify {TWITTER_API_KEY_ENVVAR} "
            f"and {TWITTER_API_SECRET_ENVVAR} environment variables"
        )
        return

    # TODO: nice fetcher


if __name__ == "__main__":
    asyncio.run(main())
