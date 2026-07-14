import discord
import os

TOKEN = os.getenv("DISCORD_TOKEN")

CHANNEL_ID = 1523123948613795974

intents = discord.Intents.default()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"{client.user} が起動しました！")

    channel = client.get_channel(CHANNEL_ID)

    if channel:
        await channel.send("🌸 プリキュアニュースBot 起動テスト！")
    else:
        print("チャンネルが見つかりませんでした")

    await client.close()


client.run(TOKEN)
