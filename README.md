![](https://img.shields.io/github/repo-size/YoshiYoshiPro/IDEA)
![](https://img.shields.io/github/license/YoshiYoshiPro/IDEA)
![Python version](https://img.shields.io/badge/Python-3.11.4-blue)
![pip version](https://img.shields.io/badge/pip-23.1.2-blue)
![GitHub release (latest by date)](https://img.shields.io/badge/release-v1.0-blue.svg)


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

## ライセンス
- MIT License

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
