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
    now = datetime.now(ZoneInfo("Asia/Tokyo"))

today = now.strftime("%Y-%m-%d")
md = now.strftime("%m-%d")
month = now.strftime("%m")
    event_file = f"{EVENT_FOLDER}/{month}.json"

    events = None

    if os.path.exists(event_file):
        try:
            with open(event_file, "r", encoding="utf-8") as f:
                events = json.load(f).get(md)

        except json.JSONDecodeError:
            print(f"{event_file} のJSON形式が正しくありません")
            events = None

    if events and last_posts.get("today_precure") != today:
        embed = discord.Embed(
            title="🌈 今日のプリキュア",
            color=discord.Color.magenta()
        )

        # 放送日
        if events.get("broadcast"):
            txt="\n".join(
    f"・{b['series']} 第{b['episode']}話\n「{b['title']}」（{b['year']}年）"
    if isinstance(b,dict) else f"・{b}"
    for b in events["broadcast"]
)

            embed.add_field(
                name="📺 放送日",
                value=txt,
                inline=False
            )

        # 誕生日
        if events.get("birthday"):
            txt = []

            for b in events["birthday"]:
                if "civilian_name" in b:
                    txt.append(
                        f"・{b['cure_name']}（{b['civilian_name']}）"
                    )
                else:
                    txt.append(
                        f"・{b['name']}"
                    )

            embed.add_field(
                name="🎂 誕生日",
                value="\n".join(txt),
                inline=False
            )

            for b in events["birthday"]:
                if b.get("special"):
                    name = b.get(
                        "cure_name",
                        b.get("name")
                    )

                    embed.add_field(
                        name="🎉 Happy Birthday! 🎉",
                        value=f"今日は **{name}** のお誕生日です！✨",
                        inline=False
                    )

        # 初変身記念日
        if events.get("first_transform"):
            vals = []

            for t in events["first_transform"]:
                if isinstance(t, dict):
                    vals.append(
                        f"・{t['civilian_name']}が{t['cure_name']}に初変身！"
                        f"（{t['series']} 第{t['episode']}話・{t['year']}年）"
                    )
                else:
                    vals.append(
                        f"・{t}"
                    )

            embed.add_field(
                name="✨ 初変身記念日",
                value="\n".join(vals),
                inline=False
            )

        embed.set_footer(text="Pretty Cure News Bot")

        await channel.send(embed=embed)

        last_posts["today_precure"] = today

    save_last_posts(last_posts)

    await client.close()


client.run(TOKEN)
