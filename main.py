import discord
import os
import feedparser
import json
from datetime import datetime
from zoneinfo import Zoneinfo

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1508090733301596283

RSS_URLS = {
    "プリティストア": "https://rss.app/feeds/1oU4mplx8CJl2VtR.xml",
    "プリキュアグッズ&情報": "https://rss.app/feeds/ez28j2Uuh4hHxhWr.xml",
    "プリキュア音楽&映像商品公式": "https://rss.app/feeds/13HLXlbioVHlU1iT.xml",
    "プリキュア アニメ公式": "https://rss.app/feeds/AidDSiGarIONaz7A.xml",
}

LAST_POST_FILE = "last_posts.json"
EVENT_FOLDER = "precure_events"


def get_last_posts():
    try:
        with open(LAST_POST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_last_posts(data):
    with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    last_posts = get_last_posts()

    channel = client.get_channel(CHANNEL_ID)

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

        if not any(k in latest.title for k in keywords):
            last_posts[name] = latest.link
            continue

        embed = discord.Embed(
            title="🌸 プリキュア新着情報",
            description=latest.title[:100],
            url=latest.link,
        )

        embed.add_field(
            name="📢 情報元",
            value=name,
            inline=False,
        )

        embed.add_field(
            name="🔗 投稿URL",
            value=latest.link,
            inline=False,
        )

        embed.set_footer(text="Pretty Cure News Bot")

        await channel.send(embed=embed)

        last_posts[name] = latest.link
    # 今日のプリキュア
    # 今日のプリ
