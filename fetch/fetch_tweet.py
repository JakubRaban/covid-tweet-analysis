import asyncio
import os

from fetch import twitter

TWITTER_API_KEY_ENVVAR = "TWITTER_API_KEY"
TWITTER_API_SECRET_ENVVAR = "TWITTER_API_SECRET"


async def main():
    api_key = os.getenv(TWITTER_API_KEY_ENVVAR)
    secret_key = os.getenv(TWITTER_API_SECRET_ENVVAR)
    if not api_key or not secret_key:
        print(
            f"You must specify {TWITTER_API_KEY_ENVVAR} "
            f"and {TWITTER_API_SECRET_ENVVAR} environment variables"
        )
        return

    client = await twitter.Client.from_api_key(api_key, secret_key, "dev")
    query = twitter.Query(query_string="koronawirus", max_results=200)
    async for tweet in client.query(query):
        print(tweet)


if __name__ == "__main__":
    asyncio.run(main())
