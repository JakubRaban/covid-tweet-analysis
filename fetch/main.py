import asyncio
import os
from datetime import datetime
from collections import namedtuple

import click

from fetch import twitter, database

TWITTER_API_KEY_ENVVAR = "TWITTER_API_KEY"
TWITTER_API_SECRET_ENVVAR = "TWITTER_API_SECRET"
TWITTER_API_DEV_ENV_ENVVAR = "TWITTER_API_DEV_ENV"
MONGODB_CONNECTION_URL_ENVVAR = "MONGODB_CONNECTION_URL"
MONGODB_DBNAME_ENVVAR = "MONGODB_DBNAME"


async def fetch(query, source, database, collection):
    async for tweet in source.query(query):
        await database.insert(tweet, collection)


async def main(query, twitter_api, collection, product, max_tweets):
    if twitter_api:
        credentials = twitter.Credentials(
            api_key=os.getenv(TWITTER_API_KEY_ENVVAR),
            secret_key=os.getenv(TWITTER_API_SECRET_ENVVAR),
            dev_env=os.getenv(TWITTER_API_DEV_ENV_ENVVAR),
        )
        if not all(credentials):
            print(
                f"You must specify {TWITTER_API_KEY_ENVVAR}, {TWITTER_API_DEV_ENV_ENVVAR} "
                f"and {TWITTER_API_SECRET_ENVVAR} environment variables"
            )
            return

        if product == '7day':
            source = await twitter.StandardClient.from_api_key(credentials)
            twitter_query = twitter.StandardQuery(query_string=query, max_results=max_tweets)
        else:
            source = await twitter.PremiumClient.from_api_key(credentials)
            source.product = product
            twitter_query = twitter.PremiumQuery(query_string=query, to_date=datetime(2020, 4, 20),
                                                 from_date=datetime(2020, 4, 16), max_results=max_tweets)

    else:
        source = twitter.FakeClient()

    db = database.DatabaseConnection.connect(
        os.getenv(MONGODB_CONNECTION_URL_ENVVAR), os.getenv(MONGODB_DBNAME_ENVVAR)
    )

    await fetch(twitter_query, source, db, collection)


@click.command()
@click.option(
    "--query",
    "-q",
    prompt="Query",
    help="Query sent to Twitter API, as specified in its documentation",
)
@click.option(
    "--twitter_api", "-t", is_flag=True, help="Use Twitter API instead of fake data"
)
@click.option(
    "--mongo_collection",
    "-c",
    default="Influencerzy",
    help="Mongo collection to insert tweets to",
)
@click.option(
    '--endpoint-product',
    '-p',
    default='7day',
    type=click.Choice(['7day', '30day', 'fullarchive']),
    help='Twitter API endpoint product'
)
@click.option(
    '--max-tweets',
    '-m',
    default=10000,
    help='Maximum number of tweets to fetch'
)
def fetch_command(query, twitter_api, mongo_collection, endpoint_product, max_tweets):
    asyncio.run(main(query, twitter_api, mongo_collection, endpoint_product, max_tweets))


if __name__ == "__main__":
    fetch_command()
