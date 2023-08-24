# インストールした discord.py を読み込む
import discord

# アクセストークンを読み込み
import env

# インテントの設定
intents = discord.Intents.all()

# 接続に必要なオブジェクトを生成
client = discord.Client(intents=intents)


# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print(f"{client.user}がログインしました")


# メッセージ受信時に動作する処理
@client.event
async def on_message(message: discord.Message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author == client.user:
        return
    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content.startswith("/neko"):
        await message.channel.send("にゃーん")


# Botの起動とDiscordサーバーへの接続
client.run(env.BOT_TOKEN)
