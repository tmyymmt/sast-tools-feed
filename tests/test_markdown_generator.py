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


def test_render_html_escapes_title():
    result = render_html("A & B <Test>", "# Hello")
    assert "A &amp; B &lt;Test&gt;" in result
    assert "<title>A & B <Test></title>" not in result


def test_render_html_sanitizes_script_and_js_url():
    result = render_html("T", '<script>alert(1)</script><a href="javascript:alert(1)">x</a>')
    assert "<script>" not in result
    assert 'href="javascript:alert(1)"' not in result


def test_render_html_sanitizer_does_not_wrap_fragment_with_html_body():
    result = render_html("T", "<div>ok</div>")
    assert "<body><html>" not in result
    assert "<body><body>" not in result


def test_generate_tool_page_type_with_distribution_field():
    """distributionフィールドが指定された場合、_tool_typeがそれを使う。"""
    tool_hybrid = {**TOOL, "distribution": "hybrid"}
    result = generate_tool_page(tool_hybrid, [])
    assert "OSS / SaaS" in result


def test_generate_tool_page_type_oss_from_distribution():
    tool_oss = {**TOOL, "distribution": "oss"}
    result = generate_tool_page(tool_oss, [])
    assert "| Type | OSS |" in result


def test_generate_tool_page_type_saas_fallback():
    """distributionフィールドがない場合はsaasフラグにフォールバックする。"""
    result = generate_tool_page(TOOL, [])
    assert "| Type | SaaS |" in result


def test_generate_tool_page_escapes_tool_name_and_description():
    tool = {**TOOL, "name": "A <B>", "description": "<img src=x onerror=1>"}
    result = generate_tool_page(tool, [])
    assert "# A &lt;B&gt;" in result
    assert "> &lt;img src=x onerror=1&gt;" in result


def test_generate_tool_page_ja_escapes_tool_name_and_description():
    tool = {**TOOL, "name": "A <B>", "description_ja": "<script>alert(1)</script>"}
    result = generate_tool_page_ja(tool, [])
    assert "# A &lt;B&gt;" in result
    assert "> &lt;script&gt;alert(1)&lt;/script&gt;" in result


def test_generate_comparison_page_escapes_tool_name_for_markdown_table():
    tool = {**TOOL, "name": "A | B ] [ <tag>"}
    result = generate_comparison_page([tool], {"semgrep": ENTRIES})
    assert "A &#124; B &#93; &#91; &lt;tag&gt;" in result


def test_generate_comparison_page_escapes_unique_features_for_markdown_table():
    tool = {**TOOL, "unique_features": ["X | Y <img src=x>"]}
    result = generate_comparison_page([tool], {"semgrep": ENTRIES})
    assert "X &#124; Y &lt;img src=x&gt;" in result


def test_generate_comparison_page_ja_escapes_unique_features_for_markdown_table():
    tool = {**TOOL, "unique_features_ja": ["A | B <script>"]}
    result = generate_comparison_page_ja([tool], {"semgrep": ENTRIES})
    assert "A &#124; B &lt;script&gt;" in result
