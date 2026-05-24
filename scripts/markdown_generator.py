"""ツールごとのまとめページおよび比較ページをMarkdownで生成する。"""
import html as _html
from datetime import datetime, timezone
from typing import Dict, List, Optional

import markdown as _md_lib
from bs4 import BeautifulSoup

from scripts.models import ReleaseEntry

_HTML_STYLE = """
  body { font-family: sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; line-height: 1.6; }
  nav { margin-bottom: 1.5em; }
  h1 { border-bottom: 2px solid #333; padding-bottom: 0.3em; }
  h2, h3 { border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #ccc; padding: 0.5em 1em; text-align: left; }
  th { background: #f5f5f5; }
  a { color: #0066cc; }
  code { background: #f0f0f0; padding: 0.1em 0.3em; border-radius: 3px; font-size: 0.9em; }
  pre code { display: block; padding: 1em; overflow: auto; }
  blockquote { border-left: 4px solid #ddd; margin: 0; padding-left: 1em; color: #666; }
  hr { border: none; border-top: 1px solid #eee; margin: 1.5em 0; }
  @media (prefers-color-scheme: dark) {
    body { background: #1a1a1a; color: #e0e0e0; }
    h1 { border-bottom-color: #555; }
    h2, h3 { border-bottom-color: #444; }
    th, td { border-color: #444; }
    th { background: #2a2a2a; }
    a { color: #4da6ff; }
    code { background: #2a2a2a; }
    blockquote { border-left-color: #555; color: #aaa; }
    hr { border-top-color: #444; }
  }
"""


def render_html(title: str, md_content: str, lang: str = "en") -> str:
    """MarkdownをHTMLページに変換する。"""
    body_html = _md_lib.markdown(md_content, extensions=["tables", "fenced_code"])
    body_html = _sanitize_html_fragment(body_html)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{_html.escape(title)}</title>
  <style>{_HTML_STYLE}</style>
</head>
<body>
  <nav><a href="index.html">&larr; SAST Tools Feed</a></nav>
{body_html}
</body>
</html>"""


def _sanitize_html_fragment(html_fragment: str) -> str:
    soup = BeautifulSoup(html_fragment, "html.parser")
    for tag in soup.find_all(["script", "style", "iframe", "object", "embed", "link", "meta"]):
        tag.decompose()
    for tag in soup.find_all(True):
        for attr in list(tag.attrs.keys()):
            value = tag.attrs.get(attr)
            if attr.lower().startswith("on"):
                del tag.attrs[attr]
                continue
            if attr.lower() in ("href", "src") and isinstance(value, str):
                if value.strip().lower().startswith(("javascript:", "data:")):
                    del tag.attrs[attr]
    if soup.body:
        return soup.body.decode_contents()
    return soup.decode_contents()

BOOL_MARK: Dict[bool, str] = {True: "✅", False: "❌"}


def _latest_entry(entries: List[ReleaseEntry]) -> Optional[ReleaseEntry]:
    return entries[0] if entries else None


def _homepage(tool: dict) -> str:
    hp = tool.get("homepage", tool.get("url", ""))
    if not hp:
        repo = tool.get("repo", "")
        hp = f"https://github.com/{repo}" if repo else ""
    return f"[{hp}]({hp})" if hp else "—"


def _tool_type(tool: dict) -> str:
    dist = tool.get("distribution")
    if dist:
        return {"oss": "OSS", "saas": "SaaS", "hybrid": "OSS / SaaS"}.get(dist.lower(), dist)
    return "SaaS" if tool.get("features", {}).get("saas") else "OSS"


def _feature_mark(tool: dict, key: str) -> str:
    return BOOL_MARK.get(tool.get("features", {}).get(key, False), "—")


def _releases_url(tool: dict) -> str:
    if tool.get("type") == "github":
        repo = tool.get("repo", "")
        return f"https://github.com/{repo}/releases" if repo else ""
    return tool.get("url", "")


def _features_url(tool: dict) -> str:
    return tool.get("features_url", tool.get("homepage", ""))


def _pricing_str(tool: dict) -> str:
    pricing = str(tool.get("pricing", "—"))
    pricing_url = str(tool.get("pricing_url", "")).strip()
    pricing_free_url = str(tool.get("pricing_free_url", "")).strip()
    pricing_paid_url = str(tool.get("pricing_paid_url", "")).strip()
    if " / " in pricing and pricing_free_url and pricing_paid_url:
        free_text, paid_text = pricing.split(" / ", 1)
        return (
            f"[{_escape_markdown_table_text(free_text)}]({pricing_free_url})"
            f" / "
            f"[{_escape_markdown_table_text(paid_text)}]({pricing_paid_url})"
        )
    if "paid" in pricing.lower() and pricing_url:
        return f"[{_escape_markdown_table_text(pricing)}]({pricing_url})"
    return _escape_markdown_table_text(pricing)


def generate_tool_page(tool: dict, entries: List[ReleaseEntry]) -> str:
    """ツールごとのまとめページ（英語）を生成する。"""
    name = _html.escape(tool["name"])
    latest = _latest_entry(entries)
    latest_version = latest.version if latest else "—"
    last_updated = latest.published_at[:10] if latest else "—"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    description = _html.escape(tool.get("description", ""))

    lines = [
        f"# {name}",
        "",
        f"> {description}",
        "",
        "## Overview",
        "",
        "| Item | Value |",
        "|------|-------|",
        f"| Type | {_tool_type(tool)} |",
        f"| License | {tool.get('license', '—')} |",
        f"| Pricing | {_pricing_str(tool)} |",
        f"| Homepage | {_homepage(tool)} |",
        f"| Latest Version | {latest_version} |",
        f"| Last Updated | {last_updated} |",
        "",
        "## Features",
        "",
        "| Feature | Supported |",
        "|---------|-----------|",
        f"| Multi-Language Support | {_feature_mark(tool, 'multi_language')} |",
        f"| Dataflow / Taint Analysis | {_feature_mark(tool, 'dataflow_taint')} |",
        f"| IDE Plugin | {_feature_mark(tool, 'ide_plugin')} |",
        f"| CI/CD Plugin | {_feature_mark(tool, 'ci_cd_plugin')} |",
        f"| Custom Rules | {_feature_mark(tool, 'custom_rules')} |",
        f"| SaaS / Cloud Version | {_feature_mark(tool, 'saas')} |",
        f"| API Server | {_feature_mark(tool, 'api_server')} |",
        f"| Dashboard | {_feature_mark(tool, 'dashboard')} |",
        f"| Centralized Management | {_feature_mark(tool, 'centralized_management')} |",
        f"| SARIF Output | {_feature_mark(tool, 'sarif_output')} |",
        f"| Auto-Fix | {_feature_mark(tool, 'auto_fix')} |",
        f"| IaC Scanning | {_feature_mark(tool, 'iac')} |",
        "",
        f"**Feature reference:** [Official Documentation]({_features_url(tool)})",
        "",
        "## Release History",
        "",
        f"**Source:** [{_releases_url(tool)}]({_releases_url(tool)})",
        "",
    ]

    if not entries:
        lines.append("*No release data available.*")
        lines.append("")
    else:
        for entry in entries:
            date = entry.published_at[:10]
            lines.append(f"### {entry.version} — {date} `{entry.category}`")
            lines.append("")
            if entry.summary:
                lines.append(entry.summary)
                lines.append("")
            if entry.body and entry.body.strip():
                lines.append(entry.body.strip())
                lines.append("")
            lines.append("---")
            lines.append("")

    lines.append(f"*Generated at {now}*")
    lines.append("")

    return "\n".join(lines)


def generate_tool_page_ja(tool: dict, entries: List[ReleaseEntry]) -> str:
    """ツールごとのまとめページ（日本語）を生成する。"""
    name = _html.escape(tool["name"])
    latest = _latest_entry(entries)
    latest_version = latest.version if latest else "—"
    last_updated = latest.published_at[:10] if latest else "—"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    description = _html.escape(tool.get("description_ja", tool.get("description", "")))

    lines = [
        f"# {name}",
        "",
        f"> {description}",
        "",
        "## 基本情報",
        "",
        "| 項目 | 内容 |",
        "|------|------|",
        f"| 種別 | {_tool_type(tool)} |",
        f"| ライセンス | {tool.get('license', '—')} |",
        f"| 費用 | {_pricing_str(tool)} |",
        f"| 公式サイト | {_homepage(tool)} |",
        f"| 最新バージョン | {latest_version} |",
        f"| 最終更新日 | {last_updated} |",
        "",
        "## 機能",
        "",
        "| 機能 | 対応 |",
        "|------|------|",
        f"| 多言語サポート | {_feature_mark(tool, 'multi_language')} |",
        f"| データフロー/テイント解析 | {_feature_mark(tool, 'dataflow_taint')} |",
        f"| IDEプラグイン | {_feature_mark(tool, 'ide_plugin')} |",
        f"| CI/CDプラグイン | {_feature_mark(tool, 'ci_cd_plugin')} |",
        f"| カスタムルール | {_feature_mark(tool, 'custom_rules')} |",
        f"| SaaS/クラウド版 | {_feature_mark(tool, 'saas')} |",
        f"| APIサーバー | {_feature_mark(tool, 'api_server')} |",
        f"| ダッシュボード | {_feature_mark(tool, 'dashboard')} |",
        f"| 集中管理 | {_feature_mark(tool, 'centralized_management')} |",
        f"| SARIF出力 | {_feature_mark(tool, 'sarif_output')} |",
        f"| 自動修正 | {_feature_mark(tool, 'auto_fix')} |",
        f"| IaCスキャン | {_feature_mark(tool, 'iac')} |",
        "",
        f"**機能一覧の情報源:** [公式ドキュメント]({_features_url(tool)})",
        "",
        "## リリース履歴",
        "",
        f"**情報源:** [{_releases_url(tool)}]({_releases_url(tool)})",
        "",
    ]

    if not entries:
        lines.append("*リリースデータがありません。*")
        lines.append("")
    else:
        for entry in entries:
            date = entry.published_at[:10]
            lines.append(f"### {entry.version} — {date} `{entry.category}`")
            lines.append("")
            if entry.summary:
                lines.append(entry.summary)
                lines.append("")
            if entry.body and entry.body.strip():
                lines.append(entry.body.strip())
                lines.append("")
            lines.append("---")
            lines.append("")

    lines.append(f"*{now} 時点の情報*")
    lines.append("")

    return "\n".join(lines)


_DETAILED_FEATURES = [
    "multi_language", "dataflow_taint", "ide_plugin", "ci_cd_plugin", "custom_rules", "saas",
    "api_server", "dashboard", "centralized_management", "sarif_output", "auto_fix", "iac",
]


def _feature_count_for_keys(tool: dict, keys: List[str]) -> int:
    return sum(1 for k in keys if tool.get("features", {}).get(k, False))


def _language_count(tool: dict) -> int:
    return len(tool.get("languages", []))


def _sort_key(tool: dict, feature_keys: List[str]) -> tuple:
    return (-_feature_count_for_keys(tool, feature_keys), -_language_count(tool), tool["name"].lower())


def _sort_tools(tools: list) -> list:
    return sorted(tools, key=lambda t: _sort_key(t, _DETAILED_FEATURES))


def _sort_tools_summary(tools: list) -> list:
    return sorted(tools, key=lambda t: _sort_key(t, _DETAILED_FEATURES))


def _unique_features_str(tool: dict) -> str:
    items = tool.get("unique_features", [])
    return "<br>".join(f"• {_escape_markdown_table_text(str(f))}" for f in items) if items else "—"


def _unique_features_str_ja(tool: dict) -> str:
    items = tool.get("unique_features_ja", tool.get("unique_features", []))
    return "<br>".join(f"• {_escape_markdown_table_text(str(f))}" for f in items) if items else "—"


def _languages_str(tool: dict) -> str:
    items = tool.get("languages", [])
    return ", ".join(_escape_markdown_table_text(str(lang)) for lang in items) if items else "—"


def _escape_markdown_table_text(text: str) -> str:
    return _html.escape(text).replace("|", "&#124;")


def _escape_markdown_link_text(text: str) -> str:
    return _escape_markdown_table_text(text).replace("[", "&#91;").replace("]", "&#93;")


def generate_comparison_page(tools: list, entries_by_tool: Dict[str, List[ReleaseEntry]]) -> str:
    """全ツール比較ページ（英語）を生成する。"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary_tools = _sort_tools_summary(tools)
    detailed_tools = _sort_tools(tools)

    lines = [
        "# SAST Tools Comparison",
        "",
        f"*Generated at {now}*",
        "",
        "## Summary",
        "",
        "| Tool | Latest | Updated | Type | License | Pricing | Languages | Multi-Lang | Dataflow | Custom Rules | SARIF | Centralized Mgmt |",
        "|------|--------|---------|------|---------|---------|-----------|------------|----------|--------------|-------|------------------|",
    ]

    for tool in summary_tools:
        tid = tool["id"]
        tool_name = _escape_markdown_link_text(tool["name"])
        latest = _latest_entry(entries_by_tool.get(tid, []))
        version = latest.version if latest else "—"
        updated = latest.published_at[:10] if latest else "—"
        lines.append(
            f"| [{tool_name}]({tid}.html)<br>[Features ↗]({_features_url(tool)})"
            f" | {version}"
            f" | {updated}"
            f" | {_tool_type(tool)}"
            f" | {tool.get('license', '—')}"
            f" | {_pricing_str(tool)}"
            f" | {_languages_str(tool)}"
            f" | {_feature_mark(tool, 'multi_language')}"
            f" | {_feature_mark(tool, 'dataflow_taint')}"
            f" | {_feature_mark(tool, 'custom_rules')}"
            f" | {_feature_mark(tool, 'sarif_output')}"
            f" | {_feature_mark(tool, 'centralized_management')} |"
        )

    lines += [
        "",
        "## Detailed Comparison",
        "",
        "| Tool | Languages | Multi-Lang | Dataflow | IDE Plugin | CI/CD Plugin | Custom Rules | SaaS | API Server | Dashboard | Centralized Mgmt | SARIF | Auto-Fix | IaC | Unique Features |",
        "|------|-----------|------------|----------|------------|--------------|--------------|------|------------|-----------|------------------|-------|----------|-----|-----------------|",
    ]

    for tool in detailed_tools:
        tid = tool["id"]
        tool_name = _escape_markdown_link_text(tool["name"])
        lines.append(
            f"| [{tool_name}]({tid}.html)<br>[Features ↗]({_features_url(tool)})"
            f" | {_languages_str(tool)}"
            f" | {_feature_mark(tool, 'multi_language')}"
            f" | {_feature_mark(tool, 'dataflow_taint')}"
            f" | {_feature_mark(tool, 'ide_plugin')}"
            f" | {_feature_mark(tool, 'ci_cd_plugin')}"
            f" | {_feature_mark(tool, 'custom_rules')}"
            f" | {_feature_mark(tool, 'saas')}"
            f" | {_feature_mark(tool, 'api_server')}"
            f" | {_feature_mark(tool, 'dashboard')}"
            f" | {_feature_mark(tool, 'centralized_management')}"
            f" | {_feature_mark(tool, 'sarif_output')}"
            f" | {_feature_mark(tool, 'auto_fix')}"
            f" | {_feature_mark(tool, 'iac')}"
            f" | {_unique_features_str(tool)} |"
        )

    lines.append("")
    return "\n".join(lines)


def generate_comparison_page_ja(tools: list, entries_by_tool: Dict[str, List[ReleaseEntry]]) -> str:
    """全ツール比較ページ（日本語）を生成する。"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary_tools = _sort_tools_summary(tools)
    detailed_tools = _sort_tools(tools)

    lines = [
        "# SASTツール比較",
        "",
        f"*{now} 時点の情報*",
        "",
        "## 概要版",
        "",
        "| ツール | 最新版 | 更新日 | 種別 | ライセンス | 費用 | 対応言語 | 多言語 | データフロー | カスタムルール | SARIF | 集中管理 |",
        "|--------|--------|--------|------|-----------|------|----------|--------|-------------|--------------|-------|---------|",
    ]

    for tool in summary_tools:
        tid = tool["id"]
        tool_name = _escape_markdown_link_text(tool["name"])
        latest = _latest_entry(entries_by_tool.get(tid, []))
        version = latest.version if latest else "—"
        updated = latest.published_at[:10] if latest else "—"
        lines.append(
            f"| [{tool_name}]({tid}_ja.html)<br>[機能一覧 ↗]({_features_url(tool)})"
            f" | {version}"
            f" | {updated}"
            f" | {_tool_type(tool)}"
            f" | {tool.get('license', '—')}"
            f" | {_pricing_str(tool)}"
            f" | {_languages_str(tool)}"
            f" | {_feature_mark(tool, 'multi_language')}"
            f" | {_feature_mark(tool, 'dataflow_taint')}"
            f" | {_feature_mark(tool, 'custom_rules')}"
            f" | {_feature_mark(tool, 'sarif_output')}"
            f" | {_feature_mark(tool, 'centralized_management')} |"
        )

    lines += [
        "",
        "## 詳細版",
        "",
        "| ツール | 対応言語 | 多言語 | データフロー | IDEプラグイン | CI/CDプラグイン | カスタムルール | SaaS | APIサーバー | ダッシュボード | 集中管理 | SARIF | 自動修正 | IaC | 独自機能 |",
        "|--------|----------|--------|-------------|--------------|----------------|--------------|------|------------|--------------|---------|-------|---------|-----|---------|",
    ]

    for tool in detailed_tools:
        tid = tool["id"]
        tool_name = _escape_markdown_link_text(tool["name"])
        lines.append(
            f"| [{tool_name}]({tid}_ja.html)<br>[機能一覧 ↗]({_features_url(tool)})"
            f" | {_languages_str(tool)}"
            f" | {_feature_mark(tool, 'multi_language')}"
            f" | {_feature_mark(tool, 'dataflow_taint')}"
            f" | {_feature_mark(tool, 'ide_plugin')}"
            f" | {_feature_mark(tool, 'ci_cd_plugin')}"
            f" | {_feature_mark(tool, 'custom_rules')}"
            f" | {_feature_mark(tool, 'saas')}"
            f" | {_feature_mark(tool, 'api_server')}"
            f" | {_feature_mark(tool, 'dashboard')}"
            f" | {_feature_mark(tool, 'centralized_management')}"
            f" | {_feature_mark(tool, 'sarif_output')}"
            f" | {_feature_mark(tool, 'auto_fix')}"
            f" | {_feature_mark(tool, 'iac')}"
            f" | {_unique_features_str_ja(tool)} |"
        )

    lines.append("")
    return "\n".join(lines)
