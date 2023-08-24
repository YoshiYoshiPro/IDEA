# IDEA - IdeaxTech非公式DiscordBot
Idea×Techの非公式AIアシスタントです。  
ChatGPTのAPIとSerpAPI（予定）を活用して最新情報もキャッチアップしています。

[discordpy](https://github.com/Rapptz/discord.py)をテンプレート元として拡張しています。

## 使用言語
- Python

## ライブラリ
- discordpy
- openai
- python-dotenv
- isort
- black（後に変更するかも）

## 開発ツール
- github codespace または remote conteiner(docker)

## 検証
ローカル環境下で`.env`ファイルをルートディレクトリに作成して、
```
BOT_TOKEN=<ボットのトークン>
OPENAI_API_KEY=<OpenAIのAPIキー>
```
を設定

## 起動コマンド
`
python ./discord_bot/main.py
`

## パッケージインストール
`
pip install -r requirements.txt
`

## デプロイ先
- Railway（現状）
