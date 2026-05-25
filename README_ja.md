# SAST Tools Feed
静的コード解析ツールのリリース情報を集約し、ツールごとのまとめページや比較ページをHTMLで生成し、フィードとして公開するリポジトリです。

🌐 **公開サイト**: https://tmyymmt.github.io/sast-tools-feed/

## 対象ツールのカテゴリ

本リポジトリは **SAST（Static Application Security Testing）ツール**（静的コード解析セキュリティツールとも呼ばれる）を対象とします。

これらのツールはプログラムを実行せずに、ソースコード・バイトコード・AST（抽象構文木）のパターンを解析し、潜在的なセキュリティ脆弱性・バグ・コード品質問題を検出します。

以下のカテゴリは**対象外**です。

- **SCA（Software Composition Analysis）**：依存ライブラリ・パッケージの脆弱性を検出するツール（例：Trivy、Grype）
  - https://github.com/tmyymmt/sca-tools-feed/
- **DAST（Dynamic Application Security Testing）**：実行中のシステムにリクエストを送信して脆弱性を検出するツール（例：OWASP ZAP）
  - https://github.com/tmyymmt/dast-tools-feed/

## 動作の仕組み

- 以下のいずれかの方法で、フィードファイルと HTML ページ（Markdownソースから生成）を更新します。
  - GitHub Actionsで週次自動実行（UTC 毎週金曜 22:00）
  - Issue を作成し、Copilot にPRを作成させ、レビュー完了後にmainへマージ

## 対象ツール

| ツール | 種別 | ライセンス |
|--------|------|----------|
| [SonarQube](https://www.sonarsource.com/products/sonarqube/) | OSS / SaaS | LGPL-3.0 |
| [Semgrep](https://semgrep.dev) | OSS / SaaS | LGPL-2.1 |
| [CodeQL](https://codeql.github.com) | OSS / GitHub Advanced Security | MIT |
| [PMD](https://pmd.github.io) | OSS | BSD-style |
| [Bandit](https://bandit.readthedocs.io) | OSS | Apache-2.0 |
| [Brakeman](https://brakemanscanner.org) | OSS | MIT |
| [gosec](https://github.com/securego/gosec) | OSS | Apache-2.0 |
| [SpotBugs](https://spotbugs.github.io) | OSS | LGPL-3.0 |

## フィード URL

### 全ツール統合

| フォーマット | URL |
|------------|-----|
| RSS 2.0 | `https://tmyymmt.github.io/sast-tools-feed/feeds/all.rss` |
| Atom 1.0 | `https://tmyymmt.github.io/sast-tools-feed/feeds/all.atom` |
| JSON Feed 1.1 | `https://tmyymmt.github.io/sast-tools-feed/feeds/all.json` |

### ツール別フィード

`{tool_id}` を `semgrep`、`codeql`、`sonarqube`、`bandit`、`brakeman`、`gosec`、`pmd`、`spotbugs` に置き換えてください。

| フォーマット | URL |
|------------|-----|
| RSS 2.0 | `https://tmyymmt.github.io/sast-tools-feed/feeds/{tool_id}.rss` |
| Atom 1.0 | `https://tmyymmt.github.io/sast-tools-feed/feeds/{tool_id}.atom` |
| JSON Feed 1.1 | `https://tmyymmt.github.io/sast-tools-feed/feeds/{tool_id}.json` |

## ページ

- **比較ページ**: [英語](https://tmyymmt.github.io/sast-tools-feed/comparison.html) / [日本語](https://tmyymmt.github.io/sast-tools-feed/comparison_ja.html)
- **ツール別まとめ**: `https://tmyymmt.github.io/sast-tools-feed/{tool_id}.html`

## リリースカテゴリ

リリースはカテゴリで分類され、フィルタリングに使用できます。

| カテゴリ | 説明 |
|---------|------|
| `feature` | 機能追加・変更 |
| `bugfix` | バグ修正 |
| `security` | セキュリティ修正・Hotfix |
| `pricing` | 料金変更 |
| `announcement` | 告知・イベント・受賞 |
| `other` | その他 |

## リポジトリ構成

```
.
├── scripts/            # Python スクリプト
│   ├── main.py         # エントリーポイント
│   ├── models.py       # データモデル
│   ├── categorize.py   # リリース分類
│   ├── storage.py      # JSON ストレージ
│   ├── feed_generator.py   # RSS/Atom/JSON Feed 生成
│   ├── markdown_generator.py  # HTML ページ生成
│   └── collectors/     # ツール種別ごとのデータ収集
│       └── github.py   # GitHub Releases API コレクター
├── tools/
│   └── tools.yml       # ツール設定ファイル
├── data/               # 収集済みリリースデータ（JSON）
├── public/             # 生成された出力（gitignore 済み、GitHub Pages にデプロイ）
├── tests/              # テストスイート
└── docs/               # 仕様書
```

## ルール

- ドキュメントは日本語・英語の両方で作成する
  - 英語：`*.md`、日本語：`*_ja.md`
- 機能変更を行う際は全仕様書を更新する
- AIに対するルールは `.github/copilot-instructions.md` に定義する

## セットアップ

### 前提条件

- Python 3.11 以上

### インストール

```bash
# 仮想環境の作成とアクティベート
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 依存パッケージのインストール
pip install -r requirements.txt

# 開発用依存パッケージのインストール（テスト実行時のみ必要）
pip install -r requirements-dev.txt
```

## ローカル実行

### 環境変数

GitHub API を利用するために `GITHUB_TOKEN` が必要です。

```bash
export GITHUB_TOKEN=your_github_token
```

### 実行

```bash
python -m scripts.main
```

`public/` 以下の HTML ファイルと `public/feeds/` 以下のフィードファイルが更新されます。

## GitHub Actions

### 自動実行（週次）

`.github/workflows/update-feeds.yml` が毎週金曜 UTC 22:00（JST 土曜 07:00）に自動実行されます。

### 手動実行

GitHub リポジトリの **Actions** タブ → **Update Feeds** → **Run workflow** から手動実行できます。

### 必要な設定

- **Secrets**：`GITHUB_TOKEN` は GitHub Actions が自動的に提供するため、追加設定不要です。
- **Permissions**：`contents: write`（data/ へのコミット用）と `pages: write`（GitHub Pages デプロイ用）はあらかじめ設定済みです。
- **GitHub Pages**：まだ有効化されていない場合でも、初回デプロイ前にワークフローが自動で有効化します。

## ライセンス

MIT License
