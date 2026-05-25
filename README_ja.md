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

## ツール一覧（ソート順）

比較ページと本READMEのツール一覧は、以下の順序で並べます。

1. 機能列のチェックマーク数が多い順
2. 同数なら対応言語数が多い順
3. さらに同数ならアルファベット順

| ツール | チェックマーク数 | 対応言語数 |
|---|---:|---:|
| SonarQube | 12 | 12 |
| Semgrep | 10 | 13 |
| CodeQL | 10 | 11 |
| PMD | 4 | 6 |
| Bandit | 3 | 1 |
| Brakeman | 3 | 1 |
| gosec | 3 | 1 |
| SpotBugs | 3 | 1 |

## ファイル構成

### 仕様テンプレート
- GitHub Spec Kit 形式の機能仕様テンプレート：`.specify/templates/spec-template.md`

### 全仕様書
- docs/full-specs/spec_ja.md
- 全仕様書は常に最新の仕様を反映する

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
