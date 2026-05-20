"""tests/test_markdown_generator.py"""
import pytest

from scripts.markdown_generator import (
    generate_comparison_page,
    generate_comparison_page_ja,
    generate_tool_page,
    generate_tool_page_ja,
    render_html,
)
from scripts.models import ReleaseEntry

TOOL = {
    "id": "semgrep",
    "name": "Semgrep",
    "type": "github",
    "repo": "semgrep/semgrep",
    "homepage": "https://semgrep.dev",
    "license": "LGPL-2.1",
    "pricing": "Free / Paid",
    "description": "Fast, lightweight, multi-language static analysis tool.",
    "description_ja": "高速・軽量・多言語対応の静的解析ツール。",
    "features": {
        "multi_language": True,
        "dataflow_taint": True,
        "ide_plugin": True,
        "ci_cd_plugin": True,
        "custom_rules": True,
        "saas": True,
        "sarif_output": True,
        "centralized_management": True,
    },
}

ENTRIES = [
    ReleaseEntry(
        tool_id="semgrep",
        tool_name="Semgrep",
        version="v1.90.0",
        published_at="2024-03-01T00:00:00Z",
        url="https://github.com/semgrep/semgrep/releases/tag/v1.90.0",
        summary="Semgrep v1.90.0 released",
        body="## What's New\n- New rule category",
        category="feature",
    ),
    ReleaseEntry(
        tool_id="semgrep",
        tool_name="Semgrep",
        version="v1.89.0",
        published_at="2024-02-01T00:00:00Z",
        url="https://github.com/semgrep/semgrep/releases/tag/v1.89.0",
        summary="Semgrep v1.89.0 released",
        body="## Bug Fixes\n- Fixed false positive",
        category="bugfix",
    ),
]


def test_generate_tool_page_contains_latest_version():
    result = generate_tool_page(TOOL, ENTRIES)
    assert "v1.90.0" in result


def test_generate_tool_page_contains_all_versions():
    result = generate_tool_page(TOOL, ENTRIES)
    assert "v1.90.0" in result
    assert "v1.89.0" in result


def test_generate_tool_page_contains_category():
    result = generate_tool_page(TOOL, ENTRIES)
    assert "`feature`" in result
    assert "`bugfix`" in result


def test_generate_tool_page_empty_entries():
    result = generate_tool_page(TOOL, [])
    assert "No release data available." in result
    assert "—" in result  # latest version shows —


def test_generate_tool_page_contains_features():
    result = generate_tool_page(TOOL, ENTRIES)
    assert "✅" in result
    assert "LGPL-2.1" in result
    assert "Free / Paid" in result


def test_generate_tool_page_contains_sast_feature_labels():
    result = generate_tool_page(TOOL, ENTRIES)
    assert "Multi-Language Support" in result
    assert "Dataflow / Taint Analysis" in result
    assert "Custom Rules" in result
    assert "SARIF Output" in result


def test_generate_tool_page_ja_contains_japanese_headers():
    result = generate_tool_page_ja(TOOL, ENTRIES)
    assert "基本情報" in result
    assert "リリース履歴" in result
    assert "機能" in result
    assert "v1.90.0" in result


def test_generate_tool_page_ja_uses_description_ja():
    result = generate_tool_page_ja(TOOL, ENTRIES)
    assert "高速・軽量・多言語対応の静的解析ツール" in result


def test_generate_tool_page_ja_contains_sast_feature_labels():
    result = generate_tool_page_ja(TOOL, ENTRIES)
    assert "多言語サポート" in result
    assert "データフロー/テイント解析" in result
    assert "カスタムルール" in result
    assert "SARIF出力" in result


def test_generate_comparison_page_contains_all_tools():
    tools = [TOOL, {**TOOL, "id": "codeql", "name": "CodeQL"}]
    entries_by_tool = {"semgrep": ENTRIES, "codeql": []}
    result = generate_comparison_page(tools, entries_by_tool)
    assert "Semgrep" in result
    assert "CodeQL" in result
    assert "v1.90.0" in result


def test_generate_comparison_page_ja_contains_japanese_header():
    tools = [TOOL]
    result = generate_comparison_page_ja(tools, {"semgrep": ENTRIES})
    assert "SASTツール比較" in result
    assert "比較" in result


def test_generate_comparison_page_empty_entries_shows_dash():
    tools = [TOOL]
    result = generate_comparison_page(tools, {"semgrep": []})
    assert "—" in result


def test_generate_comparison_page_links_to_html():
    tools = [TOOL]
    result = generate_comparison_page(tools, {"semgrep": ENTRIES})
    assert "semgrep.html" in result
    assert ".md" not in result


def test_generate_comparison_page_ja_links_to_html():
    tools = [TOOL]
    result = generate_comparison_page_ja(tools, {"semgrep": ENTRIES})
    assert "semgrep_ja.html" in result
    assert ".md" not in result


def test_render_html_returns_html_document():
    result = render_html("Test Title", "# Hello\n\nWorld")
    assert "<!DOCTYPE html>" in result
    assert "<title>Test Title</title>" in result
    assert "<h1>Hello</h1>" in result


def test_render_html_lang_ja():
    result = render_html("テスト", "# こんにちは", lang="ja")
    assert 'lang="ja"' in result


def test_render_html_renders_table():
    md = "| A | B |\n|---|---|\n| 1 | 2 |"
    result = render_html("T", md)
    assert "<table>" in result


def test_render_html_contains_dark_mode():
    result = render_html("T", "# Hello")
    assert "prefers-color-scheme: dark" in result


def test_render_html_nav_links_to_sast_feed():
    result = render_html("T", "# Hello")
    assert "SAST Tools Feed" in result
