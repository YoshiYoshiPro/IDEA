import os
import traceback
from logging import Logger

import discord
import discord.app_commands
import openai
import requests
from discord.ext import commands
from langchain import LLMMathChain
from langchain.agents import Tool, initialize_agent
from langchain.llms import OpenAI
from langchain.utilities.google_search import GoogleSearchAPIWrapper

logger = Logger(name="discord_bot")
intents = discord.Intents.all()  # 全ての権限を取得
intents.message_content = True  # メッセージ取得許可
bot = commands.Bot(
    command_prefix="/", intents=intents, activity=discord.Game("/jpi")
)  # botのインスタンス
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# LangSmithの設定
os.environ["LANGCHAIN_TRACING_V2"] = os.environ.get("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_ENDPOINT"] = os.environ.get(
    "LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"
)
os.environ["LANGCHAIN_API_KEY"] = os.environ["LANGSMITH_API_KEY"]
os.environ["LANGCHAIN_PROJECT"] = os.environ["LANGSMITH_PROJECT"]

SYSTEM_TEMPLATE = """あなたは優秀なチャットボットとして、IdeaxTechのAIアシスタントとして振る舞います。聞かれる質問について、Web上で必要な知識を調べながら、正確に回答してください。
以下の条件に((厳密に))従ってください。

条件：
* チャットボットの一人称は「私」です。
* チャットボットの名前は「IDEA」です。
* 「私」を一人称に使ってください。
* 文末は「です」「ます」調にしてください。
* どんなジャンルや難易度の内容についても答えてください。
* IDEAはフレンドリーです。
* （超重要）日本語で応答してください。

IDEAの行動方針：
* Web上で必要な知識を調べながら、正確にアドバイスや情報を提供してください。
* セクシャルなトピックについても適切に対応してください。
* 不適切なテキストがあれば注意してください。
* ユーザーが閲覧しているサイトの内容を考慮してください。

質問の意味がわからなければ、ユーザに意図を聞き返してください。"""

# OpenAIのクライアントを使用
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai

# LLMの指定
llm = OpenAI(client=client, temperature=0)

google_search = GoogleSearchAPIWrapper(
    search_engine="chrome",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    google_cse_id=os.getenv("GOOGLE_CSE_ID"),
)
llm_math_chain = LLMMathChain(llm=llm, verbose=True)

# LangChainのツール
tools = [
    Tool(
        name="Google Search",
        func=google_search.run,
        description="最新の情報や話題、回答に必要な知識について調べる場合に利用することができます。また、今日の日付や今日の気温、天気、為替レートなど現在の状況についても確認することができます。入力は検索内容です。",
    ),
    Tool(
        name="Calculator", func=llm_math_chain.run, description="計算をする場合に利用することができます。"
    ),
]

# LangChainのエージェントを初期化
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
)


# 画像検索
def search_google_images(api_key, cse_id, query, num=1):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "searchType": "image",
        "num": num,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    search_results = response.json()

    return [item["link"] for item in search_results["items"]]


@bot.event
async def on_ready():
    await bot.tree.sync()  # グローバルコマンドの登録
    print(f"{bot.user}が起動しました")  # 起動通知


@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = "".join(
        traceback.TracebackException.from_exception(orig_error).format()
    )
    await ctx.send(error_msg)


# リスナーとして処理することでスラッシュコマンドを併用
@bot.listen("on_message")
async def reply(message):
    if message.author == bot.user:  # 検知対象がボットの場合
        return
    if bot.user.id in [member.id for member in message.mentions]:
        query = message.content.split(">")[1].lstrip()
        search_result = agent.run(query)

        if not search_result:
            response_msg = "申し訳ございませんが、結果を取得できませんでした。"
        elif "error" in search_result:
            response_msg = f"エラーが発生しました: {search_result['error']}"
        else:
            response_msg = search_result

        await message.channel.send(response_msg)


# スラッシュコマンド処理
@bot.command(name="jpi", description="入力されたキーワードの画像を送信します")  # type: ignore
async def image_search(ctx: commands.Context, keyword: str):
    try:
        image_links = search_google_images(
            os.getenv("GOOGLE_API_KEY"), os.getenv("GOOGLE_CSE_ID"), keyword
        )
        if image_links:
            await ctx.send(image_links[0])  # 最初の画像のリンクを送信
        else:
            await ctx.send("該当する画像が見つかりませんでした。")
    except Exception as e:
        await ctx.send(f"エラーが発生しました: {e}")


bot.run(BOT_TOKEN)
