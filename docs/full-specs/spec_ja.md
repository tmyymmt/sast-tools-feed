# 全仕様書

このディレクトリ以下に本プロジェクトの全仕様を記述する。

## 記述方針

- 仕様は本ファイルを起点として辿れるようにする
- 1ファイルが巨大になり、読みにくくならないように、仕様書は階層的に管理する
- 仕様の記述量が多い場合は、まず抽象度高く簡潔に記載し、詳細は子ファイルを作成しそちらに記載する
- 子ファイルを作成する場合
  - 前提情報のファイルへのリンクを付けること

---

## 1. 対象ツール

### 調査対象

| ツール | 種別 | 情報源 | 取得方法 |
|---|---|---|---|
| Semgrep | OSS | https://github.com/semgrep/semgrep | GitHub Releases API |
| CodeQL | OSS / GitHub Advanced Security | https://github.com/github/codeql-action | GitHub Releases API |
| SonarQube | OSS / SaaS（SonarCloud） | https://github.com/SonarSource/sonarqube | GitHub Releases API |
| Bandit | OSS | https://github.com/PyCQA/bandit | GitHub Releases API |
| Brakeman | OSS | https://github.com/presidentbeef/brakeman | GitHub Releases API |
| gosec | OSS | https://github.com/securego/gosec | GitHub Releases API |
| PMD | OSS | https://github.com/pmd/pmd | GitHub Releases API |
| SpotBugs | OSS | https://github.com/spotbugs/spotbugs | GitHub Releases API |

### 対象外（参考記述のみ）

以下のカテゴリのツールは対象外とする。

- **SCA（Software Composition Analysis）**：依存ライブラリ・パッケージの脆弱性を検出するツール（例：Trivy、Grype）
- **DAST（Dynamic Application Security Testing）**：実行中のシステムにリクエストを送信して脆弱性を検出するツール（例：OWASP ZAP）

---

## 2. フィード仕様

### フォーマット

- RSS 2.0
- Atom 1.0
- JSON Feed 1.1

の3形式すべてに対応する。

### 含める情報項目

- バージョン（タグ名）
- 日時（公開日時）
- URL（リリースページへのリンク）
- サマリ（タイトル・概要）
- 変更内容（CHANGELOG / リリースノート本文）
- リリース種別カテゴリ（後述）

### リリース種別カテゴリ

フィードはリリース種別でカテゴリ分けする。フィルタリングにも使用する。

- `feature`：機能追加・変更
- `pricing`：料金変更
- `security`：セキュリティ修正・Hotfix
  - CVE識別子、hotfix/criticalキーワード、"security"+文脈語（fix/patch/vulnerability等）、「脆弱性」、または「セキュリティ」+文脈語（修正/パッチ/脆弱性等）のいずれかが必要 — 「セキュリティ Days」等の単独使用はsecurityに分類されない
- `bugfix`：バグ修正
- `announcement`：告知・登壇・受賞等
- `other`：その他

### 更新頻度

- GitHub Actions で週次実行（毎週土曜 JST 07:00 / UTC 金曜 22:00）
- または Issue 作成 → Copilot によるPR作成 → レビュー → mainマージ

### 公開エンドポイント

- GitHub Pages で公開
- GitHub Pages が未有効化の場合、更新ワークフローがデプロイ前に自動で有効化する

---

## 3. データ収集

### 収集方式

| 対象種別 | 方法 |
|---|---|
| GitHub OSS（Semgrep・CodeQL等） | GitHub Actions + GitHub Releases API（構造化データ取得可） |

### GitHub Releases API

- エンドポイント：`https://api.github.com/repos/{owner}/{repo}/releases`
- 取得可能なフィールド：`tag_name`（バージョン）、`published_at`（日時）、`body`（CHANGELOG相当）、`html_url`
- ページネーション：`per_page=100` でリクエストし、`Link: rel="next"` を辿って全ページを取得する
- レート制限：未認証60req/時、トークンあり5000req/時；HTTP 429 および `X-RateLimit-Remaining: 0` を伴うHTTP 403 はどちらもレート制限シグナルとして扱い、今回の実行をスキップして既存データを保持する
- ドラフトリリース（`draft: true`）はスキップする；`tag_name` または `html_url` が欠けているエントリもスキップする
- `published_at` が null の場合（プレリリース等）は `created_at` をフォールバックとして使用する；どちらもない場合はスキップする
- **APIを優先し、スクレイピングは最終手段とする**（HTML変更で壊れやすいため）

### 実行方式

- ポーリング（週次定期実行）を基本とする
- イベント駆動（GitHub webhook等）は複雑性が増すため採用しない

---

## 4. データ保存・管理

- 収集データはリポジトリ内ファイルとして保存（JSONの中間形式）
- 各ソースから取得したデータをJSON（中間形式）で統一して保存し、そこからRSS/Atom/JSON Feedを生成する
  - ソース変更時の影響範囲を最小化できる
- 履歴は永久に保持・蓄積する（削除しない）
- 対象ツールはYAML等の設定ファイルで管理し、コード変更なしで追加できる構造にする
- `merge_entries` はURL単位で重複排除する（既存データ内の重複・既存との重複・新規エントリ内部の重複を除去）

---

## 5. 公開・配信

- 対象ユーザー：不特定多数
- 購読方法：RSSリーダー、またはリポジトリのファイルを直接参照
- フィルタリング：リリース種別カテゴリで絞り込み可能

### 公開 URL

https://tmyymmt.github.io/sast-tools-feed/

### 出力ファイル構成（public/）

`public/` はリポジトリには含めない（.gitignore 済み）。GitHub Actions 実行時に生成し、GitHub Pages にデプロイする。

| パス | 内容 |
|---|---|
| `feeds/all.{rss,atom,json}` | 全ツール統合フィード |
| `feeds/{tool_id}.{rss,atom,json}` | ツール別フィード（エントリがない場合でも設定済み全ツール分を空フィードとして生成） |
| `{tool_id}.html` / `{tool_id}_ja.html` | ツールごとのまとめページ（英語/日本語） |
| `comparison.html` / `comparison_ja.html` | 全ツール比較ページ（概要版テーブル＋詳細版テーブル） |
| `index.html` | トップページ（フィード一覧・比較ページへのリンク） |
| `.nojekyll` | GitHub Pages の Jekyll 処理を無効化 |

HTMLページは `prefers-color-scheme` メディアクエリでブラウザ・OS の設定を検知し、自動的にダークモードを適用する。

`index.html` のツール一覧は比較テーブルと同じソート順（機能フラグのチェックマーク数降順、同数は対応言語数降順、さらに同条件はアルファベット昇順）で並べる。

比較ページのツール一覧は、以下の順序で並べる。

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

### ツール個別ページの構成

ツール個別ページ（`{tool_id}.html` / `{tool_id}_ja.html`）には以下を含む。

- ツール概要（タイトル・説明・種別・ライセンス・ホームページリンク）
  - **種別**は tools.yml のオプションのトップレベルフィールド `distribution`（`oss` → "OSS"、`saas` → "SaaS"、`hybrid` → "OSS / SaaS"）から取得する；未設定の場合は `saas` 機能フラグにフォールバックする
- **機能表**：12 項目の機能フラグを ✅/❌ で表示
  - 多言語サポート、データフロー/テイント解析、IDEプラグイン、CI/CDプラグイン、カスタムルール、SaaS/クラウド版、APIサーバー、ダッシュボード、集中管理、SARIF出力、自動修正、IaCスキャン
- 機能一覧の情報源リンク（tools.yml の `features_url`、未設定時は `homepage` にフォールバック）
- リリース履歴（バージョン・日付・説明のリスト）
- リリース履歴見出し直下に情報源 URL リンク（上流のリリースページへのリンク）

### 比較ページの構成

比較ページ（`comparison.html` / `comparison_ja.html`）は 2 つのテーブルで構成する。

- **概要版テーブル**：ツール名（個別ページへのリンクと機能一覧リンクを含む）・最新バージョン・最終更新日・種別・ライセンス・費用・対応プログラミング言語および基本機能フラグ（多言語・データフロー・カスタムルール・SARIF）。
- **詳細版テーブル**：ツール名（個別ページへのリンクと機能一覧リンクを含む）・対応プログラミング言語・全機能フラグ・独自機能列を含む。機能フラグ一覧：
  - 多言語、データフロー、IDEプラグイン、CI/CDプラグイン、カスタムルール、SaaS、APIサーバー、ダッシュボード、集中管理、SARIF、自動修正、IaC

`tools/tools.yml` で `pricing_url` が設定され、かつ費用表記に `Paid` を含む場合、費用テキストは公式料金ページへのリンクとして表示する。

`pricing_free_url` と `pricing_paid_url` が両方設定され、費用表記に ` / ` を含む場合は、費用セルを2つのリンクとして表示する（Free部分は `pricing_free_url`、Paid部分は `pricing_paid_url`）。

概要版・詳細版の両テーブルは同じソート順を持つ（機能フラグのチェックマーク数降順、同数は対応言語数降順、さらに同条件はアルファベット順）。

---

## 6. 非機能要件

詳細は [spec-nonfunctional_ja.md](spec-nonfunctional_ja.md) を参照。

- GitHub API を優先し、スクレイピングは最終手段とする
- 障害時は部分失敗を許容し、他ツールのフィードは継続して更新する
- アトミック書き込みにより中途半端なファイルを公開しない
- HTML 出力ではツール名・ID・ページタイトルを `html.escape` でエスケープし、不正なマークアップを防ぐ
- Markdown から生成した HTML は公開前にサニタイズし、危険なタグ/属性を除去する
- `feed-failure` GitHub ラベルは存在しない場合に自動作成してからアラート Issue を作成する
