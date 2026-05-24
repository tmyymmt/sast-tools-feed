import pytest
from scripts.storage import load_entries, save_entries, merge_entries
from scripts.models import ReleaseEntry


def make_entry(tool_id="semgrep", url="https://example.com/v1.0", version="v1.0"):
    return ReleaseEntry(
        tool_id=tool_id,
        tool_name="Semgrep",
        version=version,
        published_at="2024-01-15T10:00:00Z",
        url=url,
        summary=f"Semgrep {version}",
        body="## Changes\n- fix: something",
        category="feature",
    )


def test_save_and_load_entries(tmp_path):
    entries = [make_entry()]
    path = tmp_path / "semgrep.json"
    save_entries(str(path), entries)
    loaded = load_entries(str(path))
    assert len(loaded) == 1
    assert loaded[0].url == "https://example.com/v1.0"
    assert loaded[0].tool_id == "semgrep"


def test_load_entries_returns_empty_list_when_file_missing(tmp_path):
    path = tmp_path / "nonexistent.json"
    result = load_entries(str(path))
    assert result == []


def test_merge_entries_deduplicates_by_url():
    existing = [make_entry(url="https://example.com/v1.0", version="v1.0")]
    new = [
        make_entry(url="https://example.com/v1.0", version="v1.0"),  # duplicate
        make_entry(url="https://example.com/v2.0", version="v2.0"),  # new
    ]
    merged = merge_entries(existing, new)
    assert len(merged) == 2
    urls = [e.url for e in merged]
    assert "https://example.com/v2.0" in urls
    assert urls.count("https://example.com/v1.0") == 1


def test_merge_entries_prepends_new_entries():
    existing = [make_entry(url="https://example.com/v1.0", version="v1.0")]
    new = [make_entry(url="https://example.com/v2.0", version="v2.0")]
    merged = merge_entries(existing, new)
    assert merged[0].url == "https://example.com/v2.0"


def test_save_entries_is_atomic(tmp_path):
    """アトミック書き込み: 一時ファイルが残らないことを確認する。"""
    entries = [make_entry()]
    path = tmp_path / "semgrep.json"
    save_entries(str(path), entries)
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert tmp_files == []


def test_merge_entries_updates_empty_body():
    """既存エントリの body が空で新エントリに body がある場合は更新する。"""
    existing_no_body = ReleaseEntry(
        tool_id="semgrep",
        tool_name="Semgrep",
        version="v1.90.0",
        published_at="2024-03-01T00:00:00Z",
        url="https://example.com/v1.0",
        summary="v1.90.0",
        body="",
        category="feature",
    )
    new_with_body = make_entry(url="https://example.com/v1.0", version="v1.0")
    merged = merge_entries([existing_no_body], [new_with_body])
    assert len(merged) == 1
    assert merged[0].body == "## Changes\n- fix: something"


def test_merge_entries_does_not_overwrite_existing_body():
    """既存エントリに body がある場合は上書きしない。"""
    existing = make_entry(url="https://example.com/v1.0", version="v1.0")
    new_different_body = ReleaseEntry(
        tool_id="semgrep",
        tool_name="Semgrep",
        version="v1.0",
        published_at="2024-01-15T10:00:00Z",
        url="https://example.com/v1.0",
        summary="Semgrep v1.0",
        body="different body",
        category="feature",
    )
    merged = merge_entries([existing], [new_different_body])
    assert len(merged) == 1
    assert merged[0].body == "## Changes\n- fix: something"


def test_merge_entries_deduplicates_within_new():
    """new リスト内で同一 URL が重複している場合、最初のものだけを追加する。"""
    existing = [make_entry(url="https://example.com/v1.0", version="v1.0")]
    new = [
        make_entry(url="https://example.com/v2.0", version="v2.0"),
        make_entry(url="https://example.com/v2.0", version="v2.0"),  # duplicate within new
    ]
    merged = merge_entries(existing, new)
    assert len(merged) == 2
    assert [e.url for e in merged].count("https://example.com/v2.0") == 1


def test_merge_entries_deduplicates_existing_entries():
    existing = [
        make_entry(url="https://example.com/v1.0", version="v1.0"),
        make_entry(url="https://example.com/v1.0", version="v1.0"),
    ]
    merged = merge_entries(existing, [])
    assert len(merged) == 1
    assert merged[0].url == "https://example.com/v1.0"
