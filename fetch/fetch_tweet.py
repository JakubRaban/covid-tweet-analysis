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

    bearer_token = await twitter.retrieve_bearer_token(api_key, secret_key)
    print(bearer_token)


if __name__ == "__main__":
    asyncio.run(main())
