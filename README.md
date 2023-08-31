![](https://img.shields.io/github/repo-size/YoshiYoshiPro/IDEA)
![](https://img.shields.io/github/license/YoshiYoshiPro/IDEA)
![Python version](https://img.shields.io/badge/Python-3.11.4-blue)
![pip version](https://img.shields.io/badge/pip-23.1.2-blue)
![GitHub release (latest by date)](https://img.shields.io/badge/release-v3.0-blue.svg)


# IDEA - Idea×Tech非公式Discord Bot
Idea×Techの非公式AIアシスタントIDEAです。  
LangChainを活用して最新情報も対応しています。  
`/jpi`コマンドでキーワード画像検索もできます。
> Idea×TechメンバーのGPT無課金を救いたい。  
Discord上で会話しながら不明点が解決すれば楽じゃね？

そんな思いから生まれました。

このボットは[discordpy](https://github.com/Rapptz/discord.py)をテンプレート元として拡張しています。

## 使用言語
- Python

## 主なライブラリ
- discordpy
- openai
- langchain
- google-api-python-client
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
GOOGLE_API_KEY=<Googleカスタム検索のAPIキー>
GOOGLE_CSE_ID=<Googleカスタム検索のID>
```
を設定してください。  
Googleのカスタム検索のAPIキー取得は[ここから](https://programmablesearchengine.google.com/)

## 起動コマンド
```
python ./discord_bot/main.py
```

## パッケージインストール
```
pip install -r requirements.txt
```

## デプロイ先
- Railway
