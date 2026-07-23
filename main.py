import discord
import os
import feedparser
import json
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1508090733301596283

RSS_URLS = {
    "プリティストア": "https://rss.app/feeds/1oU4mplx8CJl2VtR.xml",
    "プリキュアグッズ&情報": "https://rss.app/feeds/ez28j2Uuh4hHxhWr.xml",
    "プリキュア音楽&映像商品公式": "https://rss.app/feeds/13HLXlbioVHlU1iT.xml",
    "プリキュア アニメ公式": "https://rss.app/feeds/AidDSiGarIONaz7A.xml",
}

LAST_POST_FILE = "last_posts.json"

BROADCAST_FOLDER = "data/broadcast"
BIRTHDAY_FILE = "data/birthdays.json"
TRANSFORM_FILE = "data/first_transform.json"


def get_last_posts():
    try:
        with open(
            LAST_POST_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_last_posts(data):
    with open(
        LAST_POST_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


# 放送回検索
def load_broadcasts(md):

    results = []

    if not os.path.exists(BROADCAST_FOLDER):
        return results

    for file in os.listdir(BROADCAST_FOLDER):

        if not file.endswith(".json"):
            continue

        path = os.path.join(
            BROADCAST_FOLDER,
            file
        )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        for episode in data:

            if episode.get("broadcast_date", "")[5:] == md:
                results.append(episode)

    return results
# 誕生日検索
def load_birthdays(md):

    try:
        with open(
            BIRTHDAY_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        return data.get(md, [])

    except (FileNotFoundError, json.JSONDecodeError):
        return []


# 初変身検索
def load_transformations(md):

    try:
        with open(
            TRANSFORM_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        return data.get(md, [])

    except (FileNotFoundError, json.JSONDecodeError):
        return []


intents = discord.Intents.default()

client = discord.Client(
    intents=intents
)


@client.event
async def on_ready():

    last_posts = get_last_posts()

    channel = client.get_channel(
        CHANNEL_ID
    )

    if channel is None:
        await client.close()
        return
       # RSS新着処理

    keywords = [
        "新商品",
        "再販",
        "発売",
        "予約",
        "販売開始",
        "登場",
        "事後通販",
        "誕生日",
        "配信",
        "公開",
        "解禁",
        "イベント",
        "キャンペーン",
        "受注",
        "受注販売",
        "受注受付",
        "上映",
        "コラボ",
        "グッズ",
        "開催",
        "開始",
        "決定",
    ]

    for name, url in RSS_URLS.items():

        feed = feedparser.parse(url)

        if not feed.entries:
            continue

        latest = feed.entries[0]

        if latest.link == last_posts.get(name):
            continue

        if not any(
            k in latest.title
            for k in keywords
        ):

            last_posts[name] = latest.link
            continue

        embed = discord.Embed(
            title="🌸 プリキュア新着情報",
            description=latest.title[:100],
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
            text="Precure News Bot"
        )

        await channel.send(
            embed=embed
        )

        last_posts[name] = latest.link
        save_last_posts(last_posts)
    # 今日のプリキュア

    now = datetime.now(
        ZoneInfo("Asia/Tokyo")
    )

    today = now.strftime("%Y-%m-%d")
    md = now.strftime("%m-%d")

    broadcasts = load_broadcasts(md)
    birthdays = load_birthdays(md)
    transformations = load_transformations(md)

    if (
        broadcasts
        or birthdays
        or transformations
    ) and last_posts.get("today_precure") != today:

        embed = discord.Embed(
            title="🌈 今日のプリキュア",
            color=discord.Color.magenta()
        )

        # 放送日
        if broadcasts:

            txt = "\n".join(
                f"・{b['series']} 第{b['episode']}話\n"
                f"「{b['title']}」（{b['year']}年）"
                for b in broadcasts
            )

            embed.add_field(
                name="📺 放送日",
                value=txt,
                inline=False
            )

        # 誕生日
        if birthdays:

            txt = "\n".join(
                f"・{b['cure_name']}（{b['character']}）"
                for b in birthdays
            )

            embed.add_field(
                name="🎂 誕生日",
                value=txt,
                inline=False
            )
        # 初変身記念日
        if transformations:

            txt = "\n".join(
                f"・{t['cure_name']}（{t['character']}）\n"
                f"『{t['series']}』({t['year']}年)"
                for t in transformations
            )

            embed.add_field(
                name="✨ 初変身記念日",
                value=txt,
                inline=False
            )

        embed.set_footer(
            text="Precure News Bot"
        )

        await channel.send(
            embed=embed
        )

        last_posts["today_precure"] = today
        save_last_posts(last_posts)

    await client.close()


client.run(TOKEN)
