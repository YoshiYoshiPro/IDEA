# discordpy project template

discord botを作成するテンプレートプロジェクトです。
詳しくは[こちらのドキュメント](https://www.tokiukaze.com/blog/discord-bot-dev/)をご覧ください。

```text
.
├── README.md
├── discord_bot         # projectファイル
│       ├── env.py      # 環境変数設定関係
│       └── main.py     # discordpyスクリプト
├── doc
├── .env                # ファイルを作成し、トークンを記載する
├── poetry.lock         # poetry依存関係
└── pyproject.toml      # pythonプロジェクトにおける開発設定ファイル
```

## 使用言語
- python

## ライブラリ
- discordpy
- python-dotenv
- isort
- black

## 開発ツール
- vscode
- github codespace または remote conteiner(docker)
