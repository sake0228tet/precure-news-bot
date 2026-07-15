import discord
import os
import feedparser
import json

TOKEN = os.getenv("DISCORD_TOKEN")

CHANNEL_ID = 1523123948613795974


RSS_URLS = {
    "プリティストア": "https://rss.app/feeds/1oU4mplx8CJl2VtR.xml",
    "プリキュアグッズ&情報": "https://rss.app/feeds/ez28j2Uuh4hHxhWr.xml",
    "プリキュア音楽&映像商品公式": "https://rss.app/feeds/13HLXlbioVHlU1iT.xml",
    "プリキュア アニメ公式": "https://rss.app/feeds/AidDSiGarIONaz7A.xml",
}


LAST_POST_FILE = "last_posts.json"


def get_last_posts():
    try:
        with open(LAST_POST_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_last_posts(data):
    with open(LAST_POST_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


intents = discord.Intents.default()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"{client.user} が起動しました！")

    last_posts = get_last_posts()

    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("チャンネルが見つかりません")
        await client.close()
        return


    keywords = [
        "新商品",
        "再販",
        "発売",
        "予約",
        "販売開始",
        "登場",
        "誕生日",
        "事後通販",
        "配信",
    ]


    for name, url in RSS_URLS.items():

        feed = feedparser.parse(url)

        if not feed.entries:
            print(f"{name}: RSS取得失敗")
            continue


        latest = feed.entries[0]


        if latest.link == last_posts.get(name):
            print(f"{name}: 送信済み")
            continue


        text = latest.title


        if not any(word in text for word in keywords):
            print(f"{name}: 対象外")
            last_posts[name] = latest.link
            continue


        if "】" in text:
            title = text.split("】")[0] + "】"
            description = text.split("】", 1)[1].strip()
        else:
            title = "プリキュア新着情報"
            description = text


        description = description[:100]

        if len(description) == 100:
            description += "..."


        embed = discord.Embed(
            title=f"🌸 {title}",
            description=description,
            url=latest.link
        )


        embed.add_field(
            name="📢 情報元",
            value=name,
            inline=False
        )


        embed.add_field(
            name="🔗 投稿URL",
            value=latest.link,
            inline=False
        )


        embed.set_footer(
            text="Pretty Cure News Bot"
        )


        await channel.send(embed=embed)

        print(f"{name}: 送信しました")


        last_posts[name] = latest.link


    save_last_posts(last_posts)

    await client.close()


client.run(TOKEN)
