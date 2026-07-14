import discord
import os
import feedparser

TOKEN = os.getenv("DISCORD_TOKEN")

RSS_URL = "https://rss.app/feeds/1oU4mplx8CJl2VtR.xml"

CHANNEL_ID = 1523123948613795974

intents = discord.Intents.default()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"{client.user} が起動しました！")

    feed = feedparser.parse(RSS_URL)

    latest = feed.entries[0]

    print("タイトル:", latest.title)
    print("URL:", latest.link)

    channel = client.get_channel(CHANNEL_ID)

    await channel.send(
        f"🌸 RSSテスト\n{latest.title}\n{latest.link}"
    )

    await client.close()


client.run(TOKEN)
