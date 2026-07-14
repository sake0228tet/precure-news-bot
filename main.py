import discord
import os
import feedparser

TOKEN = os.getenv("DISCORD_TOKEN")

CHANNEL_ID = 1523123948613795974

RSS_URL = "https://rss.app/feeds/1oU4mplx8CJl2VtR.xml"

LAST_POST_FILE = "last_post.txt"


def get_last_post():
    try:
        with open(LAST_POST_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def save_last_post(url):
    with open(LAST_POST_FILE, "w") as f:
        f.write(url)


intents = discord.Intents.default()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"{client.user} が起動しました！")

    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        print("RSS取得失敗")
        await client.close()
        return

    latest = feed.entries[0]

    last_post = get_last_post()

    if latest.link == last_post:
        print("送信済みの投稿です")
        await client.close()
        return

    channel = client.get_channel(CHANNEL_ID)

    if channel:
        await channel.send(
            f"🌸 プリティストア新着\n\n"
            f"{latest.title}\n\n"
            f"{latest.link}"
        )

        save_last_post(latest.link)

        print("送信しました")

    else:
        print("チャンネルが見つかりません")

    await client.close()


client.run(TOKEN)
