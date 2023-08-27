import discord
from langchain.llms import OpenAI
import env
from discord.ext import commands
import traceback
import openai
from langchain.agents import initialize_agent, Tool
from langchain.utilities.google_search import GoogleSearchAPIWrapper
from langchain import LLMMathChain, PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

openai.api_key = env.OPENAI_API_KEY
client = openai

template = """
{history}
Human: {input}
AI:"""

prompt = PromptTemplate(input_variables=["history", "input"], template=template)

# LLMの指定
llm = OpenAI(client=client, temperature=0)

google_search = GoogleSearchAPIWrapper(
    search_engine="chrome",
    google_api_key=env.GOOGLE_API_KEY,
    google_cse_id=env.GOOGLE_CSE_ID,
)
llm_math_chain = LLMMathChain(llm=llm, verbose=True)

# LangChainのツール
tools = [
    Tool(
        name="Google Search",
        func=google_search.run,
        description="最新の情報や話題について答える場合に利用することができます。また、今日の日付や今日の気温、天気、為替レートなど現在の状況についても確認することができます。入力は検索内容です。",
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


summary_prompt = PromptTemplate(
    input_variables=["summary", "new_lines"],
    template="""
会話の行を徐々に要約し、前の要約に追加して新しい要約を返してください。

例：
現在の要約：
人間はAIに人工知能についてどう思うか尋ねます。AIは人工知能が善の力だと考えています。
新しい会話の行：
人間：なぜあなたは人工知能が善の力だと思いますか？
AI：人工知能は人間が最大限の潜在能力を発揮するのを助けるからです。
新しい要約：
人間はAIに人工知能についてどう思うか尋ねます。AIは人工知能が善の力だと考えており、それは人間が最大限の潜在能力を発揮するのを助けるからです。
例の終わり

現在の要約：
{summary}
新しい会話の行：
{new_lines}
新しい要約：
    """,
)

memory = ConversationSummaryBufferMemory(
    llm=llm, max_token_limit=200, prompt=summary_prompt  ### <--- ここでプロンプトを上書き
)


@bot.event
async def on_ready():
    print(f"{bot.user}がログインしました")  # 起動したらターミナルにログイン通知


@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = "".join(
        traceback.TracebackException.from_exception(orig_error).format()
    )
    await ctx.send(error_msg)


@bot.event
async def on_message(message):
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


bot.run(env.BOT_TOKEN)
