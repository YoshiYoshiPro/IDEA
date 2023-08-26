import discord
from langchain.llms import OpenAI
import env
from discord.ext import commands
import traceback
import openai
from langchain.agents import initialize_agent, load_tools


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

openai.api_key = env.OPENAI_API_KEY
client = openai

# LLMに前提条件を付与
agent_kwargs = {
    "suffix": """開始!ここからの会話は全て日本語で行われる。

以前のチャット履歴
{chat_history}

新しいインプット: {input}
{agent_scratchpad}""",
}

# Agentの動作を決めるPromptのテンプレート
template = """
ユーザーからのリクエストに対して与えられたToolを使って答えてください。以下のToolが与えられています。

{tools}

以下の流れに沿ってリクエストを解決に導いてください。:

Question: あなたが解決すべきリクエストです。
Thought: Actionに移る前に常に何をすべきかを考えるようにしてください。
Action: [{tool_names}]から1つだけActionとして選んでください。Actionの名前以外はここには絶対に含めてはいけません。
Action Input: Actionに入力するInputです。選択したActionに合う形にしてください。
Observation: ここにはActionの結果得られたObservationが入ります。
...(Thought/Action/Action Input/Observationは最大5回まで繰り返すことが出来ます。)
Thought: これまでのプロセスから、あなたがた最終的に答えるべき回答を最後に考えます。
Final Answer: Questionに対する最終的な答えです。かならずこのステップで回答を終了させてください。

始めてください。

Question: {input}
{agent_scratchpad}"""


# LLMの指定
llm = OpenAI(client=client, temperature=0)

# LangChainのツールをロード
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# LangChainのエージェントを初期化
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    agent_kwargs=agent_kwargs,
    verbose=True,
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
        serpapi_result = agent.run(query)

        if not serpapi_result:
            response_msg = "申し訳ございませんが、結果を取得できませんでした。"
        elif "error" in serpapi_result:
            response_msg = f"エラーが発生しました: {serpapi_result['error']}"
        else:
            response_msg = serpapi_result

        await message.channel.send(response_msg)


bot.run(env.BOT_TOKEN)
