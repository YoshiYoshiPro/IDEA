import discord
import env
from discord.ext import commands
import traceback
import openai


intents = discord.Intents.all()


bot = commands.Bot(command_prefix="/", intents=intents)

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant. The AI assistant's name is IDEA.",
    },
    {"role": "user", "content": "こんにちは。あなたは誰ですか？"},
    {"role": "assistant", "content": "私は AI アシスタントの IDEA です。なにかお手伝いできることはありますか？"},
]


@bot.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print(f"{bot.user}がログインしました")


@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = "".join(
        traceback.TracebackException.from_exception(orig_error).format()
    )
    await ctx.send(error_msg)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.id in [member.id for member in message.mentions]:
        print(message.content)
        print(message.content.split(">")[1].lstrip())
        messages.append(
            {"role": "user", "content": message.content.split(">")[1].lstrip()}
        )

        openai.api_key = env.OPENAI_API_KEY

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

        print(completion.choices[0].message.content)
        await message.channel.send(completion.choices[0].message.content)


bot.run(env.BOT_TOKEN)
