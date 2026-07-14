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

    print(latest)
    
    # 重複チェック
    last_post = get_last_post()

    if latest.link == last_post:
        print("送信済みの投稿です")
        await client.close()
        return


    # キーワードチェック
    text = latest.title

    keywords = [
        "新商品",
        "再販",
        "発売",
        "予約",
        "販売開始",
        "登場",
    ]

    if not any(word in text for word in keywords):
        print("対象外の投稿です")
        save_last_post(latest.link)
        await client.close()
        return


    # タイトルと本文を分離
    if "】" in text:
        title = text.split("】")[0] + "】"
        description = text.split("】", 1)[1].strip()
    else:
        title = "プリティストア新着"
        description = text

    # 長すぎ防止
    description = description[:2000]


    channel = client.get_channel(CHANNEL_ID)

    if channel:
        embed = discord.Embed(
            title=f"🌸 {title}",
            description=description,
            url=latest.link
        )

        embed.set_footer(
            text="Pretty Store News Bot"
        )

        await channel.send(embed=embed)

        save_last_post(latest.link)

        print("送信しました")

    else:
        print("チャンネルが見つかりません")


    await client.close()


client.run(TOKEN)
