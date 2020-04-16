import aiohttp


async def retrieve_bearer_token(api_key, api_secret_key):
    auth = aiohttp.BasicAuth(api_key, api_secret_key)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.twitter.com/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=auth,
        ) as r:
            if r.status == 403:
                raise Exception("Invaild client credentials")
            elif r.status != 200:
                raise Exception("Unknown bearer token retrieval error")

            json_response = await r.json()
            return json_response["access_token"]
