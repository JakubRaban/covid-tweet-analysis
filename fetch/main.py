import asyncio
import os
from collections import namedtuple

import click

from fetch import twitter, database

TWITTER_API_KEY_ENVVAR = "TWITTER_API_KEY"
TWITTER_API_SECRET_ENVVAR = "TWITTER_API_SECRET"
TWITTER_API_APP_NAME_ENVVAR = "TWITTER_API_APP_NAME"
MONGODB_CONNECTION_URL_ENVVAR = "MONGODB_CONNECTION_URL"
MONGODB_DBNAME_ENVVAR = "MONGDB_DBNAME"


async def fetch(query, source, database, collection):
    async for tweet in source.query(query):
        database.insert(tweet, collection)


async def main(query, twitter_api, collection):
    twitter_query = twitter.Query(query_string=query)

    if twitter_api:
        credentials = twitter.Credentials(
            api_key=os.getenv(TWITTER_API_KEY_ENVVAR),
            secret_key=os.getenv(TWITTER_API_SECRET_ENVVAR),
            app_name=os.getenv(TWITTER_API_APP_NAME_ENVVAR),
        )
        if not all(credentials):
            print(
                f"You must specify {TWITTER_API_KEY_ENVVAR}, {TWITTER_API_APP_NAME_ENVVAR} "
                f"and {TWITTER_API_SECRET_ENVVAR} environment variables"
            )
            return

        source = await twitter.Client.from_api_key(credentials)
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
    default="tweets",
    help="Mongo collection to insert tweets to",
)
def fetch_command(query, twitter_api, collection):
    asyncio.run(main(query, twitter_api, collection))


if __name__ == "__main__":
    fetch_command()
