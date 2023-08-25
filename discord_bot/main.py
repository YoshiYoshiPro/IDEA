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

# LLMの指定
llm = OpenAI(client=client, temperature=0)

# LangChainのツールをロード
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# LangChainのエージェントを初期化
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)


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
        serpapi_tool = next((tool for tool in tools if tool.name == "serpapi"), None)
        if not serpapi_tool:
            await message.channel.send("SerpAPIツールが見つかりませんでした。")
            return

        serpapi_result = agent.run(serpapi_tool.search, query)

        if not serpapi_result:
            response_msg = "申し訳ございませんが、結果を取得できませんでした。"
        elif "error" in serpapi_result:
            response_msg = f"エラーが発生しました: {serpapi_result['error']}"
        else:
            response_msg = serpapi_result

        await message.channel.send(response_msg)


bot.run(env.BOT_TOKEN)
