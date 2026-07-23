from twikit import GuestClient
import asyncio

async def test():
    client = GuestClient()

    await client.activate()

    user = await client.get_user_by_screen_name("pps_as")
    tweets = await user.get_tweets("Tweets")

    latest = tweets[0]

    print(latest.text)
    print(latest.id)

asyncio.run(test())
