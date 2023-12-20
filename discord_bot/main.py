import datetime
import os
import traceback
from logging import Logger

import app_commands
import discord
import discord.app_commands
import openai
import requests
from discord.ext import commands
from langchain import LLMMathChain
from langchain.agents import Tool, initialize_agent
from langchain.llms import (
    ConversationBufferWindowMemory,
    OpenAI,
    SystemMessagePromptTemplate,
)
from langchain.utilities.google_search import GoogleSearchAPIWrapper
from openai import AgentType
from openai_chat.models import MessagesPlaceholder

logger = Logger(name="discord_bot")
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

chain_map = {}  # type: ignore


# チェネルIDごとでチェーンを分ける（チャネルごとで会話履歴を保持するため）
def _get_chain(channel_id: str):
    if channel_id in chain_map:
        chain = chain_map[channel_id]
    else:
        system_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_TEMPLATE)
        memory = ConversationBufferWindowMemory(
            memory_key="memory", return_messages=True, k=5
        )
        chain = initialize_agent(
            tools,
            llm,
            agent=AgentType.OPENAI_MULTI_FUNCTIONS,
            verbose=False,
            memory=memory,
            agent_kwargs={
                "system_message": system_prompt,
                "extra_prompt_messages": [
                    MessagesPlaceholder(variable_name="memory"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                    SystemMessagePromptTemplate.from_template(
                        "あなたはIdeaxTechのAIアシスタントのIDEAです。正確に回答することを徹底してください。"
                    ),
                ],
            },
        )
        chain_map[channel_id] = chain

    return chain


def _get_answer(channel_id, user_name, question):
    chain = _get_chain(channel_id)
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    answer = chain.run(
        f"私の名前は`{user_name}`です。今の時間は{now}です。以上を踏まえて以下の質問に答えてください。\n\n{question}"
    )

    return answer


class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()  # 全ての権限を取得
        intents.message_content = True  # メッセージ取得許可
        super().__init__(intents=intents)
        self.bot = commands.Bot(
            command_prefix="/", intents=intents, activity=discord.Game("/img")
        )  # botのインスタンス
        self.tree = app_commands.CommandTree(self)

    # Health Check用のサーバーを立てる

    # async def setup_hook(self):
    #     self.tree.copy_global_to(guild=MY_GUILD)  # type: ignore
    #     await self.tree.sync(guild=MY_GUILD)  # type: ignore

    #     # Wait on Flask to let AppRunner's HealthCheck pass. Endpoint of HealthCheck is assumed to be set to `/ping`.
    #     app = Flask(__name__)

    #     @app.route("/")
    #     def ping():
    #         return "ack"

    #     process = Process(target=app.run, kwargs={"port": 8080, "host": "0.0.0.0"})
    #     process.start()


bot: MyClient = MyClient()


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
    logger.info(f"{bot.user} is ready!")


@bot.tree.command(name="ask", description="IDEAに質問することができます。")
async def ask_question(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True, ephemeral=False)

    try:
        answer = _get_answer(
            interaction.channel_id,
            interaction.user.name,
            question,
        )
        # 質問文を引用する
        fixed_question = "\n".join([f"> {line}" for line in question.split("\n")])

        await interaction.followup.send(f"{fixed_question}\n{answer}")
    except Exception as e:
        logger.error(e)
        await interaction.followup.send(f"問題が発生しました。後ほど質問してください。")


@bot.event
async def on_message(message: discord.Message):
    # Determines whether or not a mentions has been made. If not, it ignores it.
    if (
        not bot.user
        or message.author.id == bot.user.id
        or message.author.bot
        or bot.user.id not in [m.id for m in message.mentions]
    ):
        return

    await message.reply(
        "IdeaxTechのAIアシスタントのIDEAです。\n質問するときは`/ask`\nキーワード画像検索は`/img`を使用してください。"
    )


# 画像検索スラッシュコマンド処理
@bot.tree.command(name="img", description="入力されたキーワードの画像を送信します")  # type: ignore
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
